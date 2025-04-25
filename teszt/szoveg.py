import cv2
import numpy as np

# Create a blank image (for demonstration)
image = np.zeros((500, 500, 3), dtype=np.uint8)

# Sample measurement value
measurement = 42.7

# Format the text to display
text = f"Measurement: {measurement:.2f}"

# Define position, font, size, color, and thickness
position = (50, 100)
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1
color = (0, 255, 0)  # Green in BGR
thickness = 2

# Draw the text on the image
cv2.putText(image, text, position, font, font_scale, color, thickness)

# Show the result
cv2.imshow('Measurement Display', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
