public class Calculator {

    // md.start:simple-add
    public int add(int a, int b) {
        return a + b;
    }
    // md.end:simple-add

    public int add(int a, int b, int c) {
        return a + b + c;
    }

    public double divide(double numerator, double denominator) {
        if (denominator == 0) {
            throw new ArithmeticException("division by zero");
        }
        return numerator / denominator;
    }
}
