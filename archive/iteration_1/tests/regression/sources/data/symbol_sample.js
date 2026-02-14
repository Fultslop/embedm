/**
 * Sample JavaScript file for symbol extraction regression tests.
 */

function greet(name) {
    return "Hello, " + name + "!";
}

export class Counter {
    constructor(initial = 0) {
        this.count = initial;
    }

    increment() {
        this.count++;
    }

    getCount() {
        return this.count;
    }
}

const double = (x) => {
    return x * 2;
};
