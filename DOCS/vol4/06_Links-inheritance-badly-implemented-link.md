# Inheritance is a Badly Implemented File Link

## Or: How OOP Reinvented Symlinks, Poorly

When Unix needed to put the same file in two places, it created links. Simple. Elegant. Understood by everyone who's ever used `ln`.

When OOP needed to reuse code, it created inheritance. Complex. Confusing. Understood by no one, including the people who teach it.

## What Links Actually Do

```bash
ln -s /usr/bin/python3 /usr/local/bin/python
```

This creates a pointer. When you call `/usr/local/bin/python`, the system says "that's actually over there" and redirects you. The link doesn't pretend to BE Python. It just points to Python.

Hard links share the same inode. Symbolic links point to a path. Both concepts are simple: "this thing is actually that thing."

## What Inheritance Pretends To Do

```python
class Animal:
    def speak(self):
        return "Some sound"

class Dog(Animal):
    pass  # I'm just an Animal, right?
```

OOP textbooks tell you Dog "is-a" Animal. That inheritance creates a relationship where Dog is just a specialized Animal. Like a symlink with extra features.

This is a lie.

## What Inheritance Actually Does

Inheritance doesn't create a link. It creates a fucking Frankenstein's monster.

```python
class Parent:
    def __init__(self):
        self.value = "parent"
    
    def method(self):
        return self.value

class Child(Parent):
    def __init__(self):
        super().__init__()
        self.value = "child"  # Wait, whose value is this?
```

This isn't a link. This is:
1. Copy some code from Parent
2. Keep references to other parts
3. Allow overriding (breaking the link)
4. Maintain a hidden chain of method calls
5. Pretend it's all one coherent object

## The Symlink Test

If inheritance was actually like symlinks:

```python
# This is what we want
class Dog(Animal):
    pass

# Should be equivalent to
Dog = Animal  # Just a link!
```

But it's not. Oh no. Not even close.

```python
# What actually happens
class Dog(Animal):
    # - Dog gets its own __dict__
    # - Dog gets its own __class__
    # - Dog copies Animal's method resolution order
    # - Dog can override Animal's methods
    # - Dog can access Animal via super()
    # - Dog might or might not call Animal's __init__
    # - Dog inherits Animal's problems
    # - Dog adds its own problems
```

## The Curse Multiplies

With file links:
```bash
ln -s /usr/bin/python /usr/local/bin/python
ln -s /usr/local/bin/python ~/bin/python
```

Three names, one file. Simple.

With inheritance:
```python
class Animal:
    def speak(self):
        return "generic sound"

class Mammal(Animal):
    def speak(self):
        return f"mammal {super().speak()}"

class Dog(Mammal):
    def speak(self):
        return f"dog {super().speak()}"
```

What does `Dog().speak()` return? To know, you must:
1. Read Dog's speak method
2. Understand super()
3. Read Mammal's speak method  
4. Understand its super()
5. Read Animal's speak method
6. Mentally execute the entire chain
7. Get: "dog mammal generic sound"
8. Wonder why you became a programmer

## The Diamond of Death

Multiple inheritance is what happens when you try to hard link to two files at once:

```python
class A:
    def method(self):
        return "A"

class B(A):
    def method(self):
        return f"B {super().method()}"

class C(A):
    def method(self):
        return f"C {super().method()}"

class D(B, C):
    pass

# What does D().method() return?
# "B C A"
# WHY? Because Python's MRO is insane
# This is not a link. This is a puzzle.
```

In Unix:
```bash
ln source dest1
ln source dest2
# Both point to the same file. No puzzle. No MRO. No super().
```

## The Admission of Failure

Every OOP language eventually adds:
- Interfaces (Java)
- Protocols (Python)  
- Traits (Rust, PHP)
- Mixins (Ruby)
- Categories (Objective-C)

These are admission that inheritance doesn't work. We wanted symlinks. We built a copy-paste mechanism that breaks constantly.

## What We Should Have Done

```python
# Composition
class Dog:
    def __init__(self):
        self.animal = Animal()
    
    def speak(self):
        return f"Woof! {self.animal.speak()}"
```

Or just functions:
```python
def animal_speak():
    return "generic sound"

def dog_speak():
    return f"Woof! {animal_speak()}"
```

No inheritance. No super(). No MRO. No diamond problem. No fragile base class. No wondering what you're actually calling.

## The Truth

Inheritance is:
- Not a "is-a" relationship
- Not a link
- Not a specialization
- Not elegant

Inheritance is:
- A partial copy
- With hidden state
- And complex resolution rules
- That breaks when you change the original
- And creates puzzles instead of solutions

## The Verdict

Unix gave us links in 1970s. Simple pointers that say "the thing you want is over there."

OOP gave us inheritance in 1980s. Complex copy mechanisms that say "the thing you want is partly here, partly there, depends on the phase of the moon and the MRO and whether someone called super() and in what order and—"

We've been debugging inheritance for 40 years. Links still just work.

Maybe, just maybe, we overcomplicated things.

---

**Build with composition. Link with actual links. Leave inheritance in the 1980s where it belongs.**

*Inheritance isn't a badly implemented link. It's a badly implemented copy that wishes it was a link but can't admit it fucked up.*