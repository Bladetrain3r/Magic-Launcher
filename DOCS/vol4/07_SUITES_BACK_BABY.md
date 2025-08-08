# Inheritance: A SuiteCRM Case Study in Architectural Cancer

## The Original Sin

```php
class SugarBean {
    // 10,000 lines of everything and nothing
}
```

This isn't a base class. This is a tumor. And like all tumors, it metastasizes.

## The Inheritance Tree of Pain

Let's trace just ONE object - a simple Contact:

```php
// What you think you're getting:
class Contact {
    public $name;
    public $email;
    public $phone;
}

// What you actually get:
class Contact extends Person extends Basic extends SugarBean
            implements Bean, Trackable, Importable, ACLTarget {
    
    // Contact brings: 500 lines
    // Person adds: 2,000 lines  
    // Basic adds: 3,000 lines
    // SugarBean adds: 10,000 lines
    // Interfaces add: 5,000 lines of contracts
    // Total: 20,500 lines to store a fucking name
}
```

## The Symlink Test Applied

If inheritance was actually like symlinks:

```bash
# What we want:
ln -s SugarBean Contact
# Contact would just BE a SugarBean with a different name

# What we get instead:
cp SugarBean Contact
patch Contact < Person.diff
patch Contact < Basic.diff  
patch Contact < Contact.diff
# Now Contact is 20,000 lines of frankenstein code
```

## The Method Resolution Nightmare

Want to save a Contact? Let's trace the call:

```php
$contact->save();

// Which save() runs?
// 1. Contact::save() - Doesn't exist, check parent
// 2. Person::save() - Exists! But it calls parent::save()
// 3. Basic::save() - Exists! But it calls parent::save()
// 4. SugarBean::save() - The actual implementation
// 5. But wait! SugarBean::save() calls:
//    - $this->before_save() - Overridden in Basic
//    - $this->performSave() - Overridden in Person
//    - $this->after_save() - Overridden in Contact

// Total methods involved in one save(): 47
// Files you need to read to understand save(): 4
// Actual database operation: 1 INSERT statement
```

## The State Mutation Horror

Each inheritance layer maintains its own state:

```php
class SugarBean {
    protected $table_name = 'base';
    protected $field_defs = [];
}

class Basic extends SugarBean {
    protected $table_name = 'basic'; // Overrides parent
    // But field_defs inherits and mutates parent's array
}

class Person extends Basic {
    function __construct() {
        parent::__construct();
        $this->field_defs['first_name'] = []; // Mutating grandparent's state
        $this->table_name = 'persons'; // Override again
    }
}

class Contact extends Person {
    function __construct() {
        parent::__construct();
        // By now, field_defs has been mutated by 3 classes
        // table_name has been overridden 3 times
        // Nobody knows what the actual state is
    }
}
```

## The Diamond of Death (SuiteCRM Edition)

```php
// The multiple inheritance disaster
class Contact extends Person implements ImportableBean {
    // Person extends Basic extends SugarBean
    // ImportableBean requires importSave()
    // SugarBean already has importSave()
    // Which one wins?
}

// The "solution": More inheritance!
class ImportablePerson extends Person implements ImportableBean {
    // Now Contact extends ImportablePerson
    // We've "solved" the problem by adding another layer
}
```

## The Performance Impact

Every method call traverses the inheritance chain:

```php
$contact->getName();
// 1. Check Contact for getName() - Not found
// 2. Check Person for getName() - Not found  
// 3. Check Basic for getName() - Not found
// 4. Check SugarBean for getName() - Found!
// 5. But SugarBean::getName() calls $this->getFieldValue('name')
// 6. getFieldValue is overridden in Basic
// 7. Which calls parent::getFieldValue()
// 8. Which checks permissions (overridden in Person)
// 9. Which checks ACL (overridden in Contact)

// Inheritance chain traversal: 9 levels
// Actual operation: return $this->name;
// Time wasted: 99%
```

## The Testing Impossibility

```php
// Try to unit test Contact
class ContactTest {
    function test_save() {
        $contact = new Contact();
        // Contact requires Person
        // Person requires Basic
        // Basic requires SugarBean
        // SugarBean requires:
        // - Global $sugar_config
        // - Global $current_user
        // - Global $db connection
        // - 47 other global variables
        // - The entire application to be bootstrapped
        
        // This is not a unit test
        // This is an integration test of the entire system
        // Because inheritance coupled everything
    }
}
```

## The Customization Trap

Want to customize? You must inherit:

```php
// Your "simple" custom contact
class CustomContact extends Contact {
    // You've now inherited:
    // - 20,500 lines of code
    // - 4 levels of state mutation
    // - 47 method override possibilities
    // - Unlimited ways to break everything
    
    function save() {
        // You want to add one validation
        $this->validate(); // Your code
        parent::save();    // 47 method calls later...
    }
}
```

## The Refactoring Impossibility

```php
// Try to refactor SugarBean
class SugarBean {
    // Change any method here
    // Break 147 child classes
    // Each with their own children
    // The inheritance tree is so deep
    // You literally cannot know what will break
}

// The solution? Never refactor
// The code fossilizes
// 10,000 lines of SugarBean from 2004
// Still running in 2024
// Because nobody dares touch it
```

## The Composition Alternative (Never Taken)

```php
// What it could have been:
class Contact {
    private $storage;
    private $validator;
    private $acl;
    
    function save() {
        if ($this->validator->validate($this)) {
            $this->storage->save($this);
        }
    }
}

// 50 lines instead of 20,500
// Testable
// Understandable  
// Maintainable
// But not "enterprise-y" enough
```

## The Real Numbers

From the SuiteCRM analysis:
- **PHP Classes: 1,882**
- **Most extend SugarBean**
- **Average inheritance depth: 4-6 levels**
- **Methods per class: ~50**
- **Overridden methods: ~30%**
- **Result: 303,906 JavaScript functions trying to compensate**

## The Conclusion

SuiteCRM's 20,850:1 hostility index isn't despite inheritance - it's BECAUSE of inheritance.

Every business object (Contact, Account, Lead, etc.) inherits from SugarBean. This means:
- **You can't understand Contact without understanding SugarBean**
- **You can't test Contact without the entire system**
- **You can't modify Contact without risking everything**
- **You can't refactor anything without breaking everything**

The 771,866 lines of code? Most of it is inheritance management:
- Calling parent methods
- Overriding parent methods
- Working around parent behavior
- Fixing inheritance conflicts
- Documenting inheritance chains

## The Symlink Truth

A symlink says: "I'm not the file, the file is over there."

Inheritance says: "I am the file, but also my parent is the file, but I've changed some of it, but not all of it, and you need to understand the entire family tree to know which parts."

In SuiteCRM, every object is carrying its entire ancestry on its back. No wonder it takes 1.2GB of RAM to display 10 contacts.

## The Epitaph

```php
class SuiteCRM extends EnterpriseFramework extends Framework extends Base {
    // 771,866 lines of inheritance hell
    // To accomplish what bash does in 5 lines
    // This is not engineering
    // This is inheritance cancer
    // And it's metastasized beyond treatment
}
```

**Inheritance isn't a badly implemented symlink. It's a badly implemented copy that creates exponential complexity for zero benefit.**

SuiteCRM proves it at scale.

---

*"20,850:1 hostility index: When your inheritance tree becomes a inheritance forest fire."*