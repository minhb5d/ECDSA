// C++17 benchmark matching the Python Twisted Edwards arithmetic.
// Fixed-loop control flow does not make boost::cpp_int constant-time.

#include <boost/multiprecision/cpp_int.hpp>
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

using boost::multiprecision::cpp_int;

namespace {
constexpr int kScalarBits = 256;
struct Point { cpp_int x; cpp_int y; };
struct Curve { const char* name; cpp_int p, a, d, q; std::uint32_t h; Point g; };
struct Stats { double average, minimum, maximum, median; };

cpp_int dec(const char* value) { return cpp_int(std::string(value)); }
cpp_int mod(cpp_int value, const cpp_int& p) {
    value %= p;
    return value < 0 ? value + p : value;
}
cpp_int select_int(const cpp_int& left, const cpp_int& right, unsigned bit) {
    const cpp_int mask = -cpp_int(bit & 1U);
    return (left & ~mask) | (right & mask);
}
cpp_int mod_pow(cpp_int base, const cpp_int& exponent, const cpp_int& p) {
    cpp_int result = 1;
    base = mod(base, p);
    for (int i = kScalarBits - 1; i >= 0; --i) {
        result = mod(result * result, p);
        const cpp_int candidate = mod(result * base, p);
        result = select_int(result, candidate, static_cast<unsigned>((exponent >> i) & 1));
    }
    return result;
}
cpp_int inverse(const cpp_int& value, const Curve& curve) {
    return mod_pow(value, curve.p - 2, curve.p);
}
Point point_add(const Point& left, const Point& right, const Curve& curve) {
    const cpp_int x1x2 = mod(left.x * right.x, curve.p);
    const cpp_int y1y2 = mod(left.y * right.y, curve.p);
    const cpp_int product = mod(curve.d * x1x2 * y1y2, curve.p);
    const cpp_int x_num = mod(left.x * right.y + left.y * right.x, curve.p);
    const cpp_int y_num = mod(y1y2 - curve.a * x1x2, curve.p);
    return {
        mod(x_num * inverse(1 + product, curve), curve.p),
        mod(y_num * inverse(1 - product, curve), curve.p)
    };
}
Point select_point(const Point& left, const Point& right, unsigned bit) {
    return {select_int(left.x, right.x, bit), select_int(left.y, right.y, bit)};
}
Point scalar_multiply(cpp_int scalar, const Point& point, const Curve& curve) {
    Point result{0, 1};
    Point addend = point;
    for (int i = 0; i < kScalarBits; ++i) {
        const Point candidate = point_add(result, addend, curve);
        result = select_point(result, candidate, static_cast<unsigned>((scalar >> i) & 1));
        addend = point_add(addend, addend, curve);
    }
    return result;
}
Curve mycurve() {
    const cpp_int p = dec("114257609839544410023767157104558613875026989059481832867036707094491730349459");
    return {"MyCurve", p, p - 1, dec("235"),
        dec("14282201229943051252970894638069826734329386005944649261350544704607507843831"), 8,
        {dec("23229630557588793144094047753885861212065941738131794352686846971944134455286"),
         dec("66049623344638828349163635859251421189934856184538099437413441721098954601166")}};
}
Curve ed25519() {
    const cpp_int p = (cpp_int(1) << 255) - 19;
    return {"Ed25519", p, p - 1,
        dec("37095705934669439343138083508754565189542113879843219016388785533085940283555"),
        dec("7237005577332262213973186563042994240857116359379907606001950938285454250989"), 8,
        {dec("15112221349535400772501151409588531511454012693041857206046113283949847762202"),
         dec("46316835694926478169428394003475163141307993866256225615783033603165251855960")}};
}
std::vector<cpp_int> make_scalars(std::size_t trials, const cpp_int& upper) {
    std::mt19937_64 rng(20260510);
    std::vector<cpp_int> values;
    for (std::size_t i = 0; i < trials; ++i) {
        cpp_int value = 0;
        for (int limb = 0; limb < 4; ++limb) value = (value << 64) | rng();
        values.push_back((value % (upper - 1)) + 1);
    }
    return values;
}
Stats benchmark(const Curve& curve, const std::vector<cpp_int>& scalars) {
    std::vector<double> timings;
    cpp_int sink = 0;
    for (const cpp_int& scalar : scalars) {
        const auto start = std::chrono::steady_clock::now();
        const Point result = scalar_multiply(scalar, curve.g, curve);
        const auto end = std::chrono::steady_clock::now();
        timings.push_back(std::chrono::duration<double>(end - start).count());
        sink ^= result.x ^ result.y;
    }
    std::sort(timings.begin(), timings.end());
    const double sum = std::accumulate(timings.begin(), timings.end(), 0.0);
    const std::size_t middle = timings.size() / 2;
    const double median = timings.size() % 2 == 0 ?
        (timings[middle - 1] + timings[middle]) / 2.0 : timings[middle];
    if (sink == -1) std::cerr << sink << '\n';
    return {sum / timings.size(), timings.front(), timings.back(), median};
}
}  // namespace

int main(int argc, char** argv) {
    const std::size_t trials = argc > 1 ? static_cast<std::size_t>(std::stoul(argv[1])) : 100;
    if (trials == 0) throw std::invalid_argument("trials must be positive");
    const Curve custom = mycurve();
    const Curve reference = ed25519();
    const auto scalars = make_scalars(trials, std::min(custom.q, reference.q));
    std::cout << "C++17 fixed-loop Twisted Edwards kG benchmark\n"
              << "Warning: regularized control flow, not constant-time cpp_int arithmetic\n\n";
    std::cout << std::left << std::setw(12) << "Curve" << std::right << std::setw(10) << "Trials"
              << std::setw(16) << "Average (s)" << std::setw(16) << "Minimum (s)"
              << std::setw(16) << "Maximum (s)" << std::setw(16) << "Median (s)" << '\n';
    for (const Curve* curve : {&custom, &reference}) {
        const Stats s = benchmark(*curve, scalars);
        std::cout << std::left << std::setw(12) << curve->name << std::right << std::setw(10) << trials
                  << std::fixed << std::setprecision(7) << std::setw(16) << s.average
                  << std::setw(16) << s.minimum << std::setw(16) << s.maximum
                  << std::setw(16) << s.median << '\n';
    }
}


