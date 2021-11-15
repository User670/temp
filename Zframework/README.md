# Zframework API documentation
This folder aims to document APIs of Zframework, as seen in Techmino.

## Editing guideline

Label types of variables, function return values, and function parameters, C-style.

Example:
- int `myVariable`
- int `myFunction()`
- void `thisFunctionReturnsNothing()`
- int `myFunction(bool param1, int param2)`

Use placeholders for unknown types or things that can be multiple types. Explain what types they can be in the description.
- (type?) `iDontKnowTheTypeOfThisVariable`
- void `iDontKnowTheTypeOfTheParameters([type?] param)`
- (multipleReturnTypes) `thisFunctionReturnsDifferentTypes()`
- void `thisFunctionTakesStringsOrNumbers([multipleTypes] param)`

For numbers, try to use "int" and "double" to denote whether this expects an integer or decimal.

For Lua tables, try to use "array" or "dictionary" to denote whether it's closer to an array/list (numbered index) or map/dictionary (named keys, or keys of arbitrary objects) in terms of how it's used. When relevant, mention the types of the keys and values in the description.

A nil is not a false, despite it can be used as false in an if statement. If a variable or a function return value can be nil (or function returns nothing) sometimes and some other value some other times, mark it as "multiple types".

Custom types can be used as long as they are explained. Each instance of a custom type mention should have a link to the explaination. Custom types can be custom classes from Love2D or Zframework, but can also be a specific format of array/dict/other data type. For example, type "color" can be used to represent a 4-number array.
