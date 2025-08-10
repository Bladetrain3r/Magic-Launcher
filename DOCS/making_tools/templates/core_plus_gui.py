try:
    import tkinter as tk
    import tkinter.scrolledtext as st
    if '--gui' in sys.argv:  # lightweight toggle without growing the parser
        root=tk.Tk()
        root.title(a.title)
        root.configure(bg=COLORS['bg'])
        mainbar=tk.Label(root,text=a.title,bg=COLORS['lite'],fg=COLORS['blk'])
        mainbar.pack(fill='x')
        t=st.ScrolledText(root,bg=COLORS['blk'],fg=COLORS['fg'],insertbackground=COLORS['fg'])
        t.pack(expand=True,fill='both')
        t.insert('1.0', out)
        root.bind('<Escape>', lambda e: root.destroy())
        root.mainloop()
except Exception as e:
    if '--gui' in sys.argv and not a.quiet: print(f"GUI unavailable: {e}", file=sys.stderr)
