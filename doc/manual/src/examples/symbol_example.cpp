// Example C++ file for symbol extraction.

namespace graphics {

class Shape {
public:
    virtual double area() const = 0;
    virtual void draw() const = 0;
};

class Circle : public Shape {
public:
    Circle(double r) : radius(r) {}

    double area() const override {
        return 3.14159 * radius * radius;
    }

    void draw() const override {
        std::cout << "Drawing circle with radius " << radius << std::endl;
    }

private:
    double radius;
};

} // namespace graphics
