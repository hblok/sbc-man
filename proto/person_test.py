import unittest
from google.protobuf import json_format
from person_pb2 import Person, AddressBook


class PersonTest(unittest.TestCase):
    
    def test_create_person(self):
        """Test creating a Person message."""
        person = Person()
        person.name = "John Doe"
        person.age = 30
        person.email = "john@example.com"
        person.phone_numbers.append("555-1234")
        person.phone_numbers.append("555-5678")
        
        self.assertEqual(person.name, "John Doe")
        self.assertEqual(person.age, 30)
        self.assertEqual(person.email, "john@example.com")
        self.assertEqual(len(person.phone_numbers), 2)
    
    def test_serialize_deserialize(self):
        """Test serialization and deserialization."""
        # Create and populate
        original = Person()
        original.name = "Alice"
        original.age = 25
        original.email = "alice@example.com"
        
        # Serialize to bytes
        serialized = original.SerializeToString()
        
        # Deserialize
        deserialized = Person()
        deserialized.ParseFromString(serialized)
        
        self.assertEqual(original.name, deserialized.name)
        self.assertEqual(original.age, deserialized.age)
        self.assertEqual(original.email, deserialized.email)
    
    def test_json_conversion(self):
        """Test JSON to protobuf and back."""
        # JSON string
        json_str = '''
        {
            "name": "Bob Smith",
            "age": 35,
            "email": "bob@example.com",
            "phoneNumbers": ["555-9999"]
        }
        '''
        
        # Parse JSON to protobuf
        person = json_format.Parse(json_str, Person())
        
        self.assertEqual(person.name, "Bob Smith")
        self.assertEqual(person.age, 35)
        self.assertEqual(len(person.phone_numbers), 1)
        
        # Convert back to JSON
        json_output = json_format.MessageToJson(person)
        self.assertIn("Bob Smith", json_output)
    
    def test_address_book(self):
        """Test nested messages with AddressBook."""
        address_book = AddressBook()
        
        # Add first person
        person1 = address_book.people.add()
        person1.name = "Person One"
        person1.age = 20
        
        # Add second person
        person2 = address_book.people.add()
        person2.name = "Person Two"
        person2.age = 40
        
        self.assertEqual(len(address_book.people), 2)
        self.assertEqual(address_book.people[0].name, "Person One")
        self.assertEqual(address_book.people[1].age, 40)


if __name__ == '__main__':
    unittest.main()
