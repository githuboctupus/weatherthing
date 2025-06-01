def calculate_r_squared(y_values):
    n = len(y_values)
    x_values = list(range(1, n + 1))  # x = 1, 2, 3, ..., n

    # Calculate means
    x_mean = sum(x_values) / n
    y_mean = sum(y_values) / n

    # Calculate slope (m) and intercept (b) of regression line
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    denominator = sum((x - x_mean) ** 2 for x in x_values)
    m = numerator / denominator
    b = y_mean - m * x_mean

    # Calculate total sum of squares (SST) and residual sum of squares (SSR)
    ss_total = sum((y - y_mean) ** 2 for y in y_values)
    ss_residual = sum((y - (m * x + b)) ** 2 for x, y in zip(x_values, y_values))

    r_squared = 1 - (ss_residual / ss_total)
    return r_squared
if __name__ == "__main__":
    print(calculate_r_squared([1, 2, 3, 5, 5, 6, 7, 8, 9]))