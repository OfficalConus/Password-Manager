def bind_title_drag(canvas, on_press, on_drag):
    """Bind drag handlers on the canvas and every item drawn on it."""
    canvas.bind("<Button-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    for item in canvas.find_all():
        canvas.tag_bind(item, "<Button-1>", on_press, add="+")
        canvas.tag_bind(item, "<B1-Motion>", on_drag, add="+")
