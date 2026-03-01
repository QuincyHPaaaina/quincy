import turtle

# Set up the screen
screen = turtle.Screen()
screen.title("Bald With Hair!")
screen.bgcolor("sky blue")

# Create our artist turtle
pen = turtle.Turtle()
pen.speed(0)  # Fastest drawing speed

# --- Draw the head (big bald circle) ---
pen.penup()
pen.goto(0, -100)
pen.pendown()
pen.color("black", "peachpuff")
pen.begin_fill()
pen.circle(100)
pen.end_fill()

# --- Draw some silly hair on top ---
pen.penup()
pen.goto(-30, 90)
pen.pendown()
pen.pensize(3)
pen.color("brown")

# Hair strand 1 - curly!
for i in range(3):
    pen.circle(10, 180)
    pen.circle(-10, 180)

# Hair strand 2
pen.penup()
pen.goto(0, 100)
pen.pendown()
for i in range(4):
    pen.circle(8, 180)
    pen.circle(-8, 180)

# Hair strand 3
pen.penup()
pen.goto(30, 90)
pen.pendown()
for i in range(3):
    pen.circle(10, 180)
    pen.circle(-10, 180)

# --- Draw the eyes ---
# Left eye (white part)
pen.penup()
pen.goto(-35, 30)
pen.pendown()
pen.color("black", "white")
pen.begin_fill()
pen.circle(15)
pen.end_fill()

# Left pupil
pen.penup()
pen.goto(-30, 35)
pen.pendown()
pen.color("black", "black")
pen.begin_fill()
pen.circle(7)
pen.end_fill()

# Right eye (white part)
pen.penup()
pen.goto(25, 30)
pen.pendown()
pen.color("black", "white")
pen.begin_fill()
pen.circle(15)
pen.end_fill()

# Right pupil
pen.penup()
pen.goto(30, 35)
pen.pendown()
pen.color("black", "black")
pen.begin_fill()
pen.circle(7)
pen.end_fill()

# --- Draw a big goofy smile ---
pen.penup()
pen.goto(-40, -10)
pen.pendown()
pen.pensize(3)
pen.color("red")
pen.setheading(-60)
pen.circle(50, 120)

# --- Draw ears ---
# Left ear
pen.penup()
pen.goto(-115, -15)
pen.pendown()
pen.color("black", "peachpuff")
pen.begin_fill()
pen.circle(15)
pen.end_fill()

# Right ear
pen.penup()
pen.goto(115, -15)
pen.pendown()
pen.begin_fill()
pen.circle(15)
pen.end_fill()

# --- Add a title ---
pen.penup()
pen.goto(0, -170)
pen.pendown()
pen.color("dark blue")
pen.write("Bald With Hair!", align="center", font=("Arial", 20, "bold"))

# Hide the turtle and keep the window open
pen.hideturtle()
screen.mainloop()
