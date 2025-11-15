# Grammar

- `::=`  : definisi
- `|`    : alternatif
- `{ X }`: pengulangan 0 atau lebih kali
- `[ X ]`: opsional (0 atau 1 kali)

## 1. Program

```ebnf
<program> ::=
    <program-header> <declaration-part> <compound-statement> DOT

<program-header> ::=
    KEYWORD(program) IDENTIFIER SEMICOLON
```

## 2. Deklarasi

```ebnf
<declaration-part> ::=
    { <const-declaration> }
    { <type-declaration> }
    { <var-declaration> }
    { <subprogram-declaration> }
```

### 2.1 Deklarasi Konstanta

```ebnf
<const-declaration> ::=
    KEYWORD(konstanta) <const-item> { <const-item> }

<const-item> ::=
    IDENTIFIER '=' <const-value> SEMICOLON

<const-value> ::=
      NUMBER
    | CHAR_LITERAL
    | STRING_LITERAL
```

### 2.2 Deklarasi Tipe

```ebnf
<type-declaration> ::=
    KEYWORD(tipe) <type-item> { <type-item> }

<type-item> ::=
    IDENTIFIER '=' <type-definition> SEMICOLON

<type-definition> ::=
      <type>
    | <range>
```

### 2.3 Deklarasi Variable

```ebnf
<var-declaration> ::=
    KEYWORD(variabel) <var-item> { <var-item> }

<var-item> ::=
    <identifier-list> COLON <type> SEMICOLON

<identifier-list> ::=
    IDENTIFIER { COMMA IDENTIFIER }
```

### 2.4 Tipe Data Dasar & Array

```ebnf
<type> ::=
    KEYWORD(integer)
  | KEYWORD(real)
  | KEYWORD(boolean)
  | KEYWORD(char)
  | <array-type>

<array-type> ::=
    KEYWORD(larik) LBRACKET <range> RBRACKET KEYWORD(dari) <type>

<range> ::=
    <expression> RANGE_OPERATOR <expression>
```

## 3. Subprogram (Procedure & Function)

```ebnf
<subprogram-declaration> ::=
    <procedure-declaration>
  | <function-declaration>

<procedure-declaration> ::=
    KEYWORD(prosedur) IDENTIFIER
    [ <formal-parameter-list> ]
    SEMICOLON
    <block>
    SEMICOLON

<function-declaration> ::=
    KEYWORD(fungsi) IDENTIFIER
    [ <formal-parameter-list> ]
    COLON <type>
    SEMICOLON
    <block>
    SEMICOLON

<formal-parameter-list> ::=
    LPARENTHESIS <parameter-group>
    { SEMICOLON <parameter-group> }
    RPARENTHESIS

<parameter-group> ::=
    <identifier-list> COLON <type>

<block> ::=
    <declaration-part> <compound-statement>
```

## 4. Compound Statement & Daftar Statement

```ebnf
<compound-statement> ::=
    KEYWORD(mulai) <statement-list> KEYWORD(selesai)

<statement-list> ::=
    <statement> { SEMICOLON <statement> }

<statement> ::=
    <assignment-statement>
  | <if-statement>
  | <while-statement>
  | <for-statement>
  | <procedure/function-call>
  | <compound-statement>
```

## 5. Bentuk-bentuk Statement

### 5.1 Assignment

```ebnf
<assignment-statement> ::=
    IDENTIFIER ASSIGN_OPERATOR <expression>
```

### 5.2 If Statement

```ebnf
<if-statement> ::=
    KEYWORD(jika) <expression> KEYWORD(maka) <statement>
    [ KEYWORD(selain-itu) <statement> ]
```

### 5.3 While Statement

```ebnf
<while-statement> ::=
    KEYWORD(selama) <expression> KEYWORD(lakukan) <statement>
```

### 5.4 For Statement

```ebnf
<for-statement> ::=
    KEYWORD(untuk) IDENTIFIER ASSIGN_OPERATOR <expression>
    ( KEYWORD(ke) | KEYWORD(turun-ke) )
    <expression>
    KEYWORD(lakukan) <statement>
```

## 6. Procedure / Function Call + Parameter List

```ebnf
<procedure/function-call> ::=
    IDENTIFIER
    LPARENTHESIS [ <parameter-list> ] RPARENTHESIS

<parameter-list> ::=
    <expression> { COMMA <expression> }

<function-call> ::=
    IDENTIFIER
    LPARENTHESIS [ <parameter-list> ] RPARENTHESIS
```

## 7. Ekspresi dan Operator

```ebnf
<expression> ::=
    <simple-expression>
    [ <relational-operator> <simple-expression> ]

<relational-operator> ::=
      '='
    | '<>'
    | '<'
    | '<='
    | '>'
    | '>='
```

```ebnf
<simple-expression> ::=
    [ <unary-add-operator> ] <term>
    { <additive-operator> <term> }

<unary-add-operator> ::=
    ARITHMETIC_OPERATOR(+) 
  | ARITHMETIC_OPERATOR(-)
```

```ebnf
<additive-operator> ::=
    ARITHMETIC_OPERATOR(+) 
  | ARITHMETIC_OPERATOR(-)
  | LOGICAL_OPERATOR(atau)
```

```ebnf
<term> ::=
    <factor> { <multiplicative-operator> <factor> }

<multiplicative-operator> ::=
      ARITHMETIC_OPERATOR(*)
    | ARITHMETIC_OPERATOR(/)
    | ARITHMETIC_OPERATOR(bagi)  
    | ARITHMETIC_OPERATOR(mod)    
    | LOGICAL_OPERATOR(dan)
```

```ebnf
<factor> ::=
    IDENTIFIER
  | NUMBER
  | CHAR_LITERAL
  | STRING_LITERAL
  | LPARENTHESIS <expression> RPARENTHESIS
  | LOGICAL_OPERATOR(tidak) <factor>
  | <function-call>
```