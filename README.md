# dumb-lang

This is very minimalistic programming language.

**dumb-lang should not be considered as a "bug free" programming language with batteries
included, etc!!!**


## Installation

After you cloned this repo, try running

```
$ docker build -it dumb-lang .
```

when it gets done, run a container with `dumb-lang` image

```
$ docker run --name <fancy name> -it dumb-lang
```


## What it looks like?

### Hello world

```
# examples/hello.dumb

func main(): i32 {
    print('Hello, world\n')
    return 0
}
```

to compile this, try running `dumbc` with `build` command:

```
$ dumbc build examples/hello.dumb
```

and run

```
$ ./hello
Hello, world
```

### Mandelbrot set example

```
func fractal(re: f32, im: f32, c_re: f32, c_im: f32, num_iters: i32): i32 {
    var iter = 0
    var _re: f32 = 0
    var _im: f32 = 0

    while iter < num_iters && _re*_re + _im*_im < 4 {
        var tmp = _re*_re - _im*_im + c_re
        _im = 2*_re*_im + c_im
        _re = tmp
        iter += 1
    }

    return iter
}


func print_density(density: f32) {
    if density > 30 {
        print('*')
    } else if density > 15 {
        print('.')
    } else {
        print(' ')
    }
}


func main(): i32 {
    var x_min = -2.5
    var x_max = 1.5
    var y_min = -1.0
    var y_max = 1.0

    var width = 100
    var height = 30

    var delta_x = (x_max - x_min) / width
    var delta_y = (y_max - y_min) / height

    var i = 0
    var j = 0

    while i < height {
        j = 0
        while j < width {
            var re = x_min + delta_x * j
            var im = y_min + delta_y * i
            var density = fractal(re, im, re, im, 100)
            print_density(density)
            j += 1
        }
        print('\n')
        i += 1
    }

    return 0
}
```

Compile it:

```
$ dumbc build examples/mandelbrot.dumb
```

Result

![result](/zzag/dumb-lang/blob/master/examples/mandlebrot.png)


## Language spec

### Basic types

- `i8` - signed 8-bit integer;
- `u8` - unsigned 8-bit integer;
- `i32` - signed 32-bit integer;
- `u32` - unsigned 32-bit integer;
- `i64` - signed 64-bit integer;
- `u64` - unsigned 64-bit integer;
- `f32` - single-precision floating-point number;
- `f64` - double-precision floating-point number;
- `bool` - boolean value, `true` or `false`;
- `str` - string(single quotes or double quotes).


### Operations

#### Arithmetic operators

| Operator | Description | Example |
| -------- |:-----------:| ------- |
| + | Adds two numbers | 1 + 2 is 3 |
| - | Subtracts two numbers | 5 - 2 is 3 |
| * | Multiplies two numbers | 3 * 2 is 6 |
| / | Divides two numbers | 3 / 2 is 1 |
| % | Takes modulus | 5 % 3 is 2 |

#### Relational operators

| Operator | Description | Example |
| -------- |:-----------:| ------- |
| <  | Checks if the value of the left operand is less than value of the right operand | 1 < 2 is `true` |
| >  | Checks if the value of the left operand is greater than value of the right operand | 1 > 2 is `false` |
| <= | Checks if the value of the left operand is less or equal to the value of the right operand | 1 <= 1 is `true` |
| >= | Checks if the value of the left operand is greater or equal to the value of the right operand | 1 >= 2 is `false` |
| == | Checks if the value of the left operand is equal to the value of the right operand | 1 == 2 is `false` |
| != | Checks if the value of the left operand is not equal to the value of the right operand | 1 != 2 is `true` |

#### Logical operators

| Operator | Description | Example |
| -------- |:-----------:| ------- |
| <code>&#124;&#124;</code> | Returns `true` if either operands is `true`, otherwise, returns `false` | <code>true &#124;&#124; false</code> is `true` |
| `&&` | Returns `true` if both operands are `true`, otherwise, returns `false` | `true && false` is `false` |
| `!`  | Negates the value of the operand | `!true` is `false` |

#### Bitwise operators

| Operator | Description | Example |
| -------- |:-----------:| ------- |
| `&` | Bitwise AND operator | `x & (x - 1)` |
| <code>&#124;</code> | Bitwise OR operator | <code>x &#124; x</code> |
| `~` | Bitwise NOT operator | `~7` |
| `^` | Bitwise XOR operator | `x ^ (x - 1)` |
| `<<` | Bitwise left shift operator | `1 << 2` |
| `>>` | Bitwise right shift operator | `16 >> 2` |

#### Assignment operators

| Operator | Description | Example |
| -------- |:-----------:| ------- |
| `=` | Assigns value of right side operand to left side operand | `x = 1` |
| `+=` | Add value of left side operand and value of right side operand, then assign the result to left side operand | `x += 1` is the same as `x = x + 1` |
| `-=` | Subtract value of left side operand and value of right side operand, then assign the result to left side operand | `x -= 1` is the same as `x = x - 1` |
| `*=` | Multiply value of left side operand and value of right side operand, then assign the result to left side operand | `x *= 1` is the same as `x = x * 1` |
| `/=` | Divide value of left side operand by value of right side operand, then assign the result to left side operand | `x /= 1` is the same as `x = x / 1` |
| `%=` | Takes modulus with values of left side operand and right side operand, then assign the result to left side operand | `x %= 1` is the same as `x = x % 1` |
| `&=` | Bitwise AND assignment operator | `x &= 7` is the same as `x = x & 7` |
| <code>&#124;=</code> | Bitwise OR assignment operator | <code>x &#124;= 7</code> is the same as <code>x = x &#124; 7</code> |
| `^=` | Bitwise XOR assignment operator | `x ^= 7` is the same as `x = x ^ 7` |
| `<<=` | Bitwise left shift assignment operator | `x <<= 7` is the same as `x = x << 7` |
| `>>=` | Bitwise right shift assignment operator | `x >>= 7` is the same as `x = x >> 7` |

#### Cast operator

In order to convert one data type into another, use `as` keyword

```
<expression> as <type>
```

For example

```
var i: i32 = 3.14 as i32 # convert 3.14 into i32
```

### Variable definition

Variables are defined with keyword `var`:

```
var <name> = <initial value>

OR

var <name>: <type> = <initial value>
```

You can specify a type of the variable by adding colon following the type.
Please note that INITIAL VALUES ARE REQUIRED! The following is causing
a compilation error:

```
var pi             # COMPILATION ERROR
var pi: f32        # COMPILATION ERROR

var pi = 3.14      # OK
var pi: f32 = 3.14 # OK
```


### Conditional statement

Conditional expression `<cond>` has to be type of `bool`, parentheses are optional.

```
if <cond> {
    ... body ...
}

OR

if <cond> {
    ... body ...
} else if <cond> {
    ... body ...
}

OR

if <cond> {
    ... body ...
} else if <cond> {
    ... body ...
} else {
    ... body ...
}
```

For example,

```
if 2 == 2 { # parentheses around "2 == 2" are optional
    print('yay!')
} else {
    print('ftw?')
}
```


### Loops

Conditional expression `<cond>` has to be type of `bool`, parentheses are optional.

```
while <cond> {
    ... body ...
}
```


### Break/Continue

`break` statement ends execution of the nearest loop.
`continue` statement works like the `break` statement. But instead of forcing
termination of the nearest enclosing loop, it forces the next iteration of the
loop to take place.

For example,

```
var i = 0;
while i < 10 {
    print('holla\n')
    if i > 2 {
        break
    }
    i += 1
}
```

outputs

```
holla
holla
holla
```

### Return statement

`return` statement stops the execution of a function and returns a value, if it
was given.

```
return
return <value> # return value is optional
```

For example,

```
func sum(a: i32, b: i32): i32 {
    return a + b
}

func drink_beer(age: i32) {
    if (age < 18) {
        print("sorry, you're less than 18")
        return
    }
    # drink beer...?
}
```

### Semicolons

Semicolons are optional. For example, the following code snippets are the same:

```
i = 0;
while i < 10 {
    print('foobar');
    i += 1;
}
```

```
i = 0
while i < 10 {
    print('foobar')
    i += 1
}
```
