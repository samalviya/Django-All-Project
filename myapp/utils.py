def find_smallest_number(numbers):
    if not numbers:
        return None
    smallest_number = numbers[0]
    for number in numbers:
        if number < smallest_number:
            smallest_number = number
    return smallest_number

def find_largest_number(numbers):
    if not numbers:
        return None
    largest_number = numbers[0]
    for number in numbers:
        if number > largest_number:
            largest_number = number
    return largest_number

def calculate_sum(numbers):
    return sum(numbers)

# Add more functions as needed
