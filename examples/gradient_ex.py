from textual_pyfiglet.gradient import print_gradient, print_text_with_gradient


# Print a simple gradient bar
print_gradient("bright_red", "bright_blue", steps=40)

# # Print a longer gradient with more steps
# print_gradient("#ff5f00", "#0080ff", steps=40, width=1)

message = "You can see that the gradient will adjust to the length of the text."

# # Print text with gradient
print_text_with_gradient(message, "#ff0000", "#0000ff")
