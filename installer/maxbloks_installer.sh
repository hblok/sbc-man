#!/bin/bash

# ============================================================================
# Installer for Max Bloks SBC-Manager on Portmaster
# ============================================================================
# Supports: Debian variants, TinaLinux/OpenWrt, etc.
# Handles: Limited package managers, varying Python installations
# ============================================================================

set -e  # Exit on error (will be trapped)

# --- Constants ---
readonly APP_NAME="sbcman"
readonly APP_MAIN_MODULE="sbcman.main"
readonly APP_VERSION="0.0.57"  # TODO: Make dynamic
readonly GITHUB_WHEEL_URL="https://github.com/hblok/sbc-man/releases/download/v${APP_VERSION}/${APP_NAME}-${APP_VERSION}-py3-none-any.whl"
readonly PYGAME_MIN_VERSION="2.3.0"
readonly PYTHON_MIN_VERSION="3.7"

readonly FORCE_PYGAME="${FORCE_PYGAME:-0}"  # Set to 1 to install pygame instead of pygame-ce

# --- Color Codes (if supported) ---
if [ -t 1 ]; then
    readonly RED='\033[0;31m'
    readonly GREEN='\033[0;32m'
    readonly YELLOW='\033[1;33m'
    readonly BLUE='\033[0;34m'
    readonly NC='\033[0m' # No Color
else
    readonly RED=''
    readonly GREEN=''
    readonly YELLOW=''
    readonly BLUE=''
    readonly NC=''
fi

# --- Global Variables ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORTS_DIR="${SCRIPT_DIR}"
PYTHON_BIN=""
SITE_PACKAGES=""
INSTALL_DIR=""
TEMP_DIR=""
LOG_FILE="${PORTS_DIR}/${APP_NAME}_install.log"
SYSTEM_TYPE=""
ARCH=""
PYTHON_VERSION=""
DEBUG="${DEBUG:-0}"
OFFLINE_MODE="${OFFLINE_MODE:-0}"

# --- Utility Functions ---

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    
    if [ "$DEBUG" = "1" ] || [ "$level" != "DEBUG" ]; then
        case "$level" in
            ERROR)
                echo -e "${RED}[ERROR]${NC} $message" >&2
                ;;
            WARN)
                echo -e "${YELLOW}[WARN]${NC} $message"
                ;;
            INFO)
                echo -e "${GREEN}[INFO]${NC} $message"
                ;;
            DEBUG)
                [ "$DEBUG" = "1" ] && echo -e "${BLUE}[DEBUG]${NC} $message"
                ;;
            *)
                echo "$message"
                ;;
        esac
    fi
}

show_status() {
    local message="$1"
    echo ""
    echo "======================================"
    echo -e "${GREEN}${message}${NC}"
    echo "======================================"
    log "INFO" "$message"
}

show_progress() {
    local current="$1"
    local total="$2"
    local message="$3"
    
    local percent=$((current * 100 / total))
    local filled=$((percent / 5))
    local empty=$((20 - filled))
    
    printf "\r["
    printf "%${filled}s" | tr ' ' '#'
    printf "%${empty}s" | tr ' ' ' '
    printf "] %3d%% - %s" "$percent" "$message"
    
    if [ "$current" -eq "$total" ]; then
	echo ""
    fi
}

error_exit() {
    local message="$1"
    log "ERROR" "$message"
    echo ""
    echo -e "${RED}╔════════════════════════════════════════╗${NC}"
    echo -e "${RED}║         INSTALLATION FAILED            ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${RED}Error: ${message}${NC}"
    echo ""
    echo "Check the log file for details: $LOG_FILE"
    cleanup_on_error
    exit 1
}

check_command() {
    local cmd="$1"
    if command -v "$cmd" >/dev/null 2>&1; then
        log "DEBUG" "Command found: $cmd"
        return 0
    else
        log "DEBUG" "Command not found: $cmd"
        return 1
    fi
}

cleanup_on_error() {
    log "INFO" "Cleaning up after error..."
    if [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
        log "DEBUG" "Removed temporary directory: $TEMP_DIR"
    fi
}

cleanup() {
    log "INFO" "Performing cleanup..."
    if [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
        log "DEBUG" "Removed temporary directory: $TEMP_DIR"
    fi
}

# --- Detection Functions ---

detect_system() {
    show_status "Detecting system type..."
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        SYSTEM_TYPE="$ID"
        log "INFO" "Detected system: $NAME ($ID)"
    elif [ -f /etc/openwrt_release ]; then
        SYSTEM_TYPE="openwrt"
        log "INFO" "Detected system: OpenWrt/TinaLinux"
    else
        SYSTEM_TYPE="unknown"
        log "WARN" "Could not detect system type"
    fi
    
    log "DEBUG" "System type: $SYSTEM_TYPE"
}

detect_architecture() {
    show_status "Detecting architecture..."
    
    ARCH=$(uname -m)
    log "INFO" "Architecture: $ARCH"
    
    case "$ARCH" in
        armv7l|armhf)
            WHEEL_ARCH="armv7l"
            ;;
        aarch64|arm64)
            WHEEL_ARCH="aarch64"
            ;;
        x86_64|amd64)
            WHEEL_ARCH="x86_64"
            ;;
        i686|i386)
            WHEEL_ARCH="i686"
            ;;
        *)
            log "WARN" "Unknown architecture: $ARCH, will try generic wheels"
            WHEEL_ARCH="any"
            ;;
    esac
    
    log "DEBUG" "Wheel architecture: $WHEEL_ARCH"
}

find_python() {
    show_status "Locating Python 3..."
    
    # Try common locations
    # TODO: Make dynamic rather than hardcoded version
    local python_candidates=(
        "python3"
        "/usr/bin/python3"
        "/usr/local/bin/python3"
        "python3.11"
        "python3.10"
        "python3.9"
        "python3.8"
        "python3.7"
    )
    
    for candidate in "${python_candidates[@]}"; do
        if command -v "$candidate" >/dev/null 2>&1; then
            PYTHON_BIN="$(command -v "$candidate")"
            log "INFO" "Found Python: $PYTHON_BIN"
            break
        fi
    done
    
    if [ -z "$PYTHON_BIN" ]; then
        error_exit "Python 3 not found. Please install Python 3.7 or later."
    fi
    
    # Get Python version
    PYTHON_VERSION=$($PYTHON_BIN --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
    log "INFO" "Python version: $PYTHON_VERSION"
    
    # Check minimum version
    local py_major=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    local py_minor=$(echo "$PYTHON_VERSION" | cut -d. -f2)
    local min_major=$(echo "$PYTHON_MIN_VERSION" | cut -d. -f1)
    local min_minor=$(echo "$PYTHON_MIN_VERSION" | cut -d. -f2)
    
    if [ "$py_major" -lt "$min_major" ] || ([ "$py_major" -eq "$min_major" ] && [ "$py_minor" -lt "$min_minor" ]); then
        error_exit "Python $PYTHON_MIN_VERSION or later is required (found $PYTHON_VERSION)"
    fi
    
    log "DEBUG" "Python version check passed"
}

get_site_packages() {
    show_status "Determining Python site-packages location..."
    
    # Try to get site-packages directory
    SITE_PACKAGES=$($PYTHON_BIN -c "import site; print(site.getsitepackages()[0])" 2>/dev/null || echo "")
    
    if [ -z "$SITE_PACKAGES" ]; then
        # Fallback to user site-packages
        SITE_PACKAGES=$($PYTHON_BIN -m site --user-site 2>/dev/null || echo "")
    fi
    
    if [ -z "$SITE_PACKAGES" ]; then
        # Last resort: calculate from prefix
        local prefix=$($PYTHON_BIN -c "import sys; print(sys.prefix)")
        SITE_PACKAGES="${prefix}/lib/python${PYTHON_VERSION}/site-packages"
    fi
    
    log "INFO" "Site-packages: $SITE_PACKAGES"
    
    # Create site-packages if it doesn't exist and we have permission
    if [ ! -d "$SITE_PACKAGES" ]; then
        log "WARN" "Site-packages directory does not exist: $SITE_PACKAGES"
        if mkdir -p "$SITE_PACKAGES" 2>/dev/null; then
            log "INFO" "Created site-packages directory"
        else
            log "WARN" "Cannot create site-packages directory, will use alternative location"
            SITE_PACKAGES=""
        fi
    fi
}

check_disk_space() {
    show_status "Checking disk space..."
    
    local required_mb=100  # Estimate: 100MB required
    local available_kb=$(df "$PORTS_DIR" | tail -1 | awk '{print $4}')
    local available_mb=$((available_kb / 1024))
    
    log "INFO" "Available space: ${available_mb}MB"
    
    if [ "$available_mb" -lt "$required_mb" ]; then
        error_exit "Insufficient disk space. Required: ${required_mb}MB, Available: ${available_mb}MB"
    fi
    
    log "DEBUG" "Disk space check passed"
}

# --- Download Functions ---

download_file() {
    local url="$1"
    local dest="$2"
    local max_retries=3
    local retry=0
    
    log "INFO" "Downloading: $url"
    log "DEBUG" "Destination: $dest"
    
    while [ $retry -lt $max_retries ]; do
        if check_command wget; then
            if wget -q --show-progress --timeout=30 -O "$dest" "$url" 2>&1 | tee -a "$LOG_FILE"; then
                log "INFO" "Download successful"
                return 0
            fi
        elif check_command curl; then
            if curl -L --progress-bar --connect-timeout 30 -o "$dest" "$url" 2>&1 | tee -a "$LOG_FILE"; then
                log "INFO" "Download successful"
                return 0
            fi
        else
            error_exit "Neither wget nor curl is available for downloading"
        fi
        
        retry=$((retry + 1))
        log "WARN" "Download failed, retry $retry/$max_retries"
        sleep 2
    done
    
    return 1
}

# --- Pip Management ---

check_pip() {
    show_status "Checking for pip..."
    
    if $PYTHON_BIN -m pip --version >/dev/null 2>&1; then
        log "INFO" "pip is available"
        return 0
    elif check_command pip3; then
        log "INFO" "pip3 command is available"
        return 0
    else
        log "WARN" "pip is not available"
        return 1
    fi
}

install_pip() {
    show_status "Installing pip..."
    
    # Try ensurepip first
    if $PYTHON_BIN -m ensurepip --default-pip 2>&1 | tee -a "$LOG_FILE"; then
        log "INFO" "pip installed via ensurepip"
        return 0
    fi
    
    # Fallback: download get-pip.py
    log "INFO" "Attempting to install pip via get-pip.py"
    local get_pip="${TEMP_DIR}/get-pip.py"
    
    if download_file "https://bootstrap.pypa.io/get-pip.py" "$get_pip"; then
        if $PYTHON_BIN "$get_pip" --user 2>&1 | tee -a "$LOG_FILE"; then
            log "INFO" "pip installed successfully"
            return 0
        fi
    fi
    
    log "WARN" "Could not install pip automatically"
    return 1
}

# --- Pygame Installation ---



# --- Pygame Installation ---

install_pygame() {
    show_status "Checking for pygame..."
    
    # Check if pygame is already installed
    if $PYTHON_BIN -c "import pygame; print(pygame.version.ver)" 2>/dev/null; then
        local installed_version=$($PYTHON_BIN -c "import pygame; print(pygame.version.ver)" 2>/dev/null)
        log "INFO" "pygame is already installed (version: $installed_version)"
        
        # Check if it's pygame-ce
        if $PYTHON_BIN -c "import pygame; pygame.version.SDL" 2>/dev/null | grep -q "CE" 2>/dev/null; then
            log "INFO" "pygame-ce detected, skipping installation"
        else
            log "INFO" "pygame (classic) detected, skipping installation"
        fi
        
        return 0
    fi
    
    log "INFO" "pygame not found, proceeding with installation..."
    
    # Determine which pygame to install
    local pygame_package="pygame-ce"
    if [ "$FORCE_PYGAME" = "1" ]; then
        pygame_package="pygame"
        log "INFO" "FORCE_PYGAME flag set, will install classic pygame"
    fi
    
    show_status "Installing ${pygame_package}..."
    
    # Method 1: Try pip install
    if check_pip; then
        log "INFO" "Attempting to install ${pygame_package} via pip..."
        
        if $PYTHON_BIN -m pip install "$pygame_package" --user --no-warn-script-location 2>&1 | tee -a "$LOG_FILE"; then
            log "INFO" "${pygame_package} installed successfully via pip"
            return 0
        fi
        
        log "WARN" "pip install of ${pygame_package} failed"
        
        # If pygame-ce failed and we haven't tried regular pygame yet, try it
        if [ "$pygame_package" = "pygame-ce" ]; then
            log "INFO" "Attempting to install pygame (non-CE) as fallback..."
            
            if $PYTHON_BIN -m pip install pygame --user --no-warn-script-location 2>&1 | tee -a "$LOG_FILE"; then
                log "INFO" "pygame installed successfully via pip"
                return 0
            fi
            
            log "WARN" "pip install of pygame also failed, trying alternatives..."
        fi
    fi
    
    # Method 2: Try system package manager
    log "INFO" "Attempting to install pygame via system package manager..."
    
    case "$SYSTEM_TYPE" in
        debian|ubuntu|raspbian)
            if check_command apt-get; then
                if sudo apt-get update && sudo apt-get install -y python3-pygame 2>&1 | tee -a "$LOG_FILE"; then
                    log "INFO" "pygame installed via apt-get"
                    return 0
                fi
            fi
            ;;
        openwrt)
            if check_command opkg; then
                if opkg update && opkg install python3-pygame 2>&1 | tee -a "$LOG_FILE"; then
                    log "INFO" "pygame installed via opkg"
                    return 0
                fi
            fi
            ;;
    esac
    
    # Method 3: Check for bundled wheel (try pygame-ce first, then pygame)
    log "INFO" "Looking for bundled pygame wheel..."
    
    local wheel_patterns=("pygame_ce-*-${WHEEL_ARCH}.whl" "pygame-*-${WHEEL_ARCH}.whl")
    
    for pattern in "${wheel_patterns[@]}"; do
        local bundled_wheel="${SCRIPT_DIR}/wheels/${pattern}"
        
        if ls $bundled_wheel 1> /dev/null 2>&1; then
            local wheel_file=$(ls $bundled_wheel | head -1)
            log "INFO" "Found bundled wheel: $wheel_file"
            
            if check_pip; then
                if $PYTHON_BIN -m pip install "$wheel_file" --user --no-warn-script-location 2>&1 | tee -a "$LOG_FILE"; then
                    log "INFO" "pygame installed from bundled wheel"
                    return 0
                fi
            else
                # Manual extraction
                if extract_wheel "$wheel_file" "$SITE_PACKAGES"; then
                    log "INFO" "pygame extracted from bundled wheel"
                    return 0
                fi
            fi
        fi
    done
    
    error_exit "Failed to install pygame. Please install it manually."
}


# --- Wheel Extraction ---

extract_wheel() {
    local wheel_file="$1"
    local target_dir="$2"
    
    log "INFO" "Manually extracting wheel: $wheel_file"
    log "DEBUG" "Target directory: $target_dir"
    
    if ! check_command unzip; then
        log "ERROR" "unzip command not available for wheel extraction"
        return 1
    fi
    
    # Create target directory if needed
    mkdir -p "$target_dir" 2>/dev/null || {
        log "ERROR" "Cannot create target directory: $target_dir"
        return 1
    }
    
    # Extract wheel (wheels are zip files)
    if unzip -q -o "$wheel_file" -d "$target_dir" 2>&1 | tee -a "$LOG_FILE"; then
        log "INFO" "Wheel extracted successfully"
        return 0
    else
        log "ERROR" "Failed to extract wheel"
        return 1
    fi
}

# --- Application Installation ---

install_app() {
    show_status "Installing ${APP_NAME}..."
    
    local wheel_file="${TEMP_DIR}/${APP_NAME}-${APP_VERSION}-py3-none-any.whl"
    
    # Download application wheel
    if [ "$OFFLINE_MODE" != "1" ]; then
        log "INFO" "Downloading application wheel from GitHub..."
        if ! download_file "$GITHUB_WHEEL_URL" "$wheel_file"; then
            log "WARN" "Failed to download from GitHub, checking for bundled version..."
            wheel_file="${SCRIPT_DIR}/${APP_NAME}-${APP_VERSION}-py3-none-any.whl"
            if [ ! -f "$wheel_file" ]; then
                error_exit "Could not download or find application wheel"
            fi
        fi
    else
        log "INFO" "Offline mode: using bundled wheel"
        wheel_file="${SCRIPT_DIR}/${APP_NAME}-${APP_VERSION}-py3-none-any.whl"
        if [ ! -f "$wheel_file" ]; then
            error_exit "Bundled wheel not found: $wheel_file"
        fi
    fi
    
    # Verify wheel file exists and has content
    if [ ! -s "$wheel_file" ]; then
        error_exit "Wheel file is missing or empty: $wheel_file"
    fi
    
    log "INFO" "Wheel file ready: $wheel_file"
    
    # Try installation methods in order of preference
    local install_success=0
    
    # Method 1: pip install to user site-packages
    if check_pip && [ -n "$SITE_PACKAGES" ]; then
        log "INFO" "Attempting pip install to user site-packages..."
        if $PYTHON_BIN -m pip install "$wheel_file" --user --no-warn-script-location --force-reinstall 2>&1 | tee -a "$LOG_FILE"; then
            INSTALL_DIR=$($PYTHON_BIN -m site --user-site)
            log "INFO" "Application installed to user site-packages: $INSTALL_DIR"
            install_success=1
        fi
    fi
    
    # Method 2: pip install to system site-packages
    if [ $install_success -eq 0 ] && check_pip && [ -n "$SITE_PACKAGES" ] && [ -w "$SITE_PACKAGES" ]; then
        log "INFO" "Attempting pip install to system site-packages..."
        if $PYTHON_BIN -m pip install "$wheel_file" --force-reinstall 2>&1 | tee -a "$LOG_FILE"; then
            INSTALL_DIR="$SITE_PACKAGES"
            log "INFO" "Application installed to system site-packages: $INSTALL_DIR"
            install_success=1
        fi
    fi
    
    # Method 3: Manual extraction to site-packages
    if [ $install_success -eq 0 ] && [ -n "$SITE_PACKAGES" ] && [ -w "$SITE_PACKAGES" ]; then
        log "INFO" "Attempting manual extraction to site-packages..."
        if extract_wheel "$wheel_file" "$SITE_PACKAGES"; then
            INSTALL_DIR="$SITE_PACKAGES"
            log "INFO" "Application extracted to site-packages: $INSTALL_DIR"
            install_success=1
        fi
    fi
    
    # Method 4: Install to PORTS directory (last resort)
    if [ $install_success -eq 0 ]; then
        log "INFO" "Installing to PORTS directory as last resort..."
        INSTALL_DIR="${PORTS_DIR}/${APP_NAME}/lib"
        mkdir -p "$INSTALL_DIR"
        
        if extract_wheel "$wheel_file" "$INSTALL_DIR"; then
            log "INFO" "Application extracted to PORTS directory: $INSTALL_DIR"
            install_success=1
        fi
    fi
    
    if [ $install_success -eq 0 ]; then
        error_exit "Failed to install application using any method"
    fi
    
    log "INFO" "Application installation complete"
}

# --- Launcher Creation ---

create_launcher() {
    show_status "Creating launcher script..."
    
    local launcher="${PORTS_DIR}/${APP_NAME}.sh"
    mkdir -p "${PORTS_DIR}/${APP_NAME}"
    
    log "INFO" "Creating launcher: $launcher"
    
    cat > "$launcher" << EOF
#!/bin/bash
# Launcher for ${APP_NAME}
# Generated by installer on $(date)

# Set Python path if installed to PORTS directory
if [ -d "${INSTALL_DIR}" ] && [[ "${INSTALL_DIR}" == *"${APP_NAME}"* ]]; then
    export PYTHONPATH="${INSTALL_DIR}:\${PYTHONPATH}"
fi

# TODO: Fix python version
export PYTHONPATH=/mnt/SDCARD/System/lib/python3.11:/mnt/SDCARD/Apps/PortMaster/PortMaster/exlibs:/mnt/SDCARD/System/lib/python3.11/site-packages:\${PYTHONPATH}

# GPU settings (TODO: Figure out compatability)
export PYSDL2_DLL_PATH=/usr/lib
export SDL_VIDEODRIVER=mali
export SDL_RENDER_DRIVER=opengles2

# Launch application
exec "${PYTHON_BIN}" -m ${APP_MAIN_MODULE} >> /tmp/${APP_NAME}.log 2>&1
EOF
    
    chmod +x "$launcher"
    log "INFO" "Launcher created and made executable"
    
    # Create a symlink in the main PORTS directory for easy access
    # This will typically not work on FAT file systems
    #ln -sf "${PORTS_DIR}/${APP_NAME}/${APP_NAME}.sh" "${PORTS_DIR}/${APP_NAME}.sh" 2>/dev/null || true
}

create_portmaster_metadata() {
    show_status "Creating Portmaster metadata..."
    
    local port_dir="${PORTS_DIR}/${APP_NAME}"
    local port_file="${port_dir}/${APP_NAME}.port"
    
    log "INFO" "Creating .port file: $port_file"
    
    cat > "$port_file" << EOF
#!/bin/bash

if [ -d "/opt/system/Tools/PortMaster/" ]; then
  controlfolder="/opt/system/Tools/PortMaster"
elif [ -d "/opt/tools/PortMaster/" ]; then
  controlfolder="/opt/tools/PortMaster"
else
  controlfolder="/roms/ports/PortMaster"
fi

source \$controlfolder/control.txt

get_controls

GAMEDIR="${port_dir}"
cd \$GAMEDIR

exec > >(tee "\$GAMEDIR/log.txt") 2>&1

\$ESUDO chmod 666 /dev/uinput
export SDL_GAMECONTROLLERCONFIG="\$sdl_controllerconfig"

${PYTHON_BIN} -m ${APP_NAME}
EOF
    
    chmod +x "$port_file"
    log "INFO" "Portmaster metadata created"
}

# --- Verification ---

verify_install() {
    show_status "Verifying installation..."
    
    local verification_failed=0
    
    # Test pygame import
    log "INFO" "Testing pygame import..."
    if $PYTHON_BIN -c "import pygame" 2>/dev/null || $PYTHON_BIN -c "import pygame_ce as pygame" 2>/dev/null; then
        log "INFO" "✓ pygame import successful"
    else
        log "ERROR" "✗ pygame import failed"
        verification_failed=1
    fi
    
    # Test application import
    log "INFO" "Testing application import..."
    if $PYTHON_BIN -c "import ${APP_NAME}" 2>/dev/null; then
        log "INFO" "✓ ${APP_NAME} import successful"
    else
        log "ERROR" "✗ ${APP_NAME} import failed"
        verification_failed=1
    fi
    
    # Check launcher exists
    if [ -f "${PORTS_DIR}/${APP_NAME}.sh" ]; then
        log "INFO" "✓ Launcher script exists"
    else
        log "ERROR" "✗ Launcher script missing"
        verification_failed=1
    fi
    
    if [ $verification_failed -eq 1 ]; then
        log "WARN" "Verification completed with errors"
        return 1
    else
        log "INFO" "✓ All verification checks passed"
        return 0
    fi
}

# --- Main Installation Flow ---

show_banner() {
    clear
    cat << "EOF"
╔════════════════════════════════════════╗
║                                        ║
║     PORTMASTER GAME INSTALLER          ║
║                                        ║
╚════════════════════════════════════════╝
EOF
    echo ""
    echo "Installing: ${APP_NAME} v${APP_VERSION}"
    echo "Target: ${PORTS_DIR}"
    echo ""
}

show_completion() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                        ║${NC}"
    echo -e "${GREEN}║     INSTALLATION COMPLETED!            ║${NC}"
    echo -e "${GREEN}║                                        ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo "Installation Summary:"
    echo "  • Application: ${APP_NAME} v${APP_VERSION}"
    echo "  • Python: ${PYTHON_BIN} (${PYTHON_VERSION})"
    echo "  • Install Location: ${INSTALL_DIR}"
    echo "  • Launcher: ${PORTS_DIR}/${APP_NAME}/${APP_NAME}.sh"
    echo ""
    echo "You can now launch ${APP_NAME} from Portmaster!"
    echo ""
    echo "Log file: ${LOG_FILE}"
    echo ""
}

main() {
    # Initialize log file
    echo "=== Installation started at $(date) ===" > "$LOG_FILE"
    
    # Show banner
    show_banner
    
    # Create temporary directory
    TEMP_DIR=$(mktemp -d -t "${APP_NAME}-install.XXXXXX")
    log "DEBUG" "Created temporary directory: $TEMP_DIR"
    
    # Run installation steps
    show_progress 1 10 "Detecting system..."
    detect_system
    
    show_progress 2 10 "Detecting architecture..."
    detect_architecture
    
    show_progress 3 10 "Finding Python..."
    find_python
    
    show_progress 4 10 "Getting site-packages..."
    get_site_packages
    
    show_progress 5 10 "Checking disk space..."
    check_disk_space

    show_progress 6 10 "Checking pip..."
    if ! check_pip; then
        install_pip || log "WARN" "Continuing without pip"
    fi
    
    show_progress 7 10 "Installing pygame..."
    install_pygame
    
    show_progress 8 10 "Installing application..."
    install_app

    show_progress 9 10 "Creating launcher..."
    create_launcher
    # TODO: IMAGE
    # todo
    #create_portmaster_metadata
    
    show_progress 10 10 "Verifying installation..."
    verify_install || log "WARN" "Some verification checks failed"
    
    # Cleanup
    cleanup
    
    # Show completion message
    show_completion
    
    log "INFO" "Installation completed successfully"
    echo "=== Installation completed at $(date) ===" >> "$LOG_FILE"
}

# --- Error Handling ---
trap 'error_exit "Installation failed at line $LINENO"' ERR
trap cleanup EXIT

# --- Entry Point ---

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            cat << EOF
Usage: $0 [OPTIONS]

Options:
    --help, -h          Show this help message
    --debug             Enable debug output
    --offline           Use bundled dependencies only (no downloads)
    --force-pygame      Install classic pygame instead of pygame-ce
    
Environment Variables:
    DEBUG=1             Enable debug mode
    OFFLINE_MODE=1      Enable offline mode
    FORCE_PYGAME=1      Force classic pygame installation	
EOF
            exit 0
            ;;
        --debug)
            DEBUG=1
            shift
            ;;
        --offline)
            OFFLINE_MODE=1
            shift
            ;;
        --force-pygame)
            FORCE_PYGAME=1
            shift
            ;;
	
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run main installation
main "$@"
