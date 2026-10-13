#!/usr/bin/env python3
"""JP 0593b: Windows stage/companion password selector (no automatic warp)."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from jp_password_stage_0593 import (
    EXPECTED, PARTNERS, STAGES, decode, encode, load_tables, valid_partner,
)

# Visual order differs from the original game's encoded values.
COMPANIONS = (("None", 0), ("Alucard", 3), ("Sypha", 1), ("Grant", 2))


@dataclass(frozen=True)
class Selection:
    name: str
    stage: int
    partner: int
    hard: bool = False
    toggle: int = 0


def choices(stage: int, hard: bool, tables: dict[str, bytes]) -> dict[str, bool]:
    if not 0 <= stage < len(STAGES):
        raise ValueError("Invalid save-point index")
    return {label: valid_partner(stage, partner, int(hard), tables)
            for label, partner in COMPANIONS}


def password(value: Selection, tables: dict[str, bytes]) -> tuple[str, ...]:
    if not 0 <= value.stage < len(STAGES) or not 0 <= value.partner < len(PARTNERS):
        raise ValueError("Invalid stage or companion")
    if not valid_partner(value.stage, value.partner, int(value.hard), tables):
        raise ValueError("Companion unavailable on this route in Normal mode; "
                         "choose another stage or Hard mode (changes difficulty)")
    rows = encode(value.name, value.stage, value.partner, int(value.hard),
                  value.toggle, tables)
    expected = dict(save_point=value.stage, partner=value.partner,
                    hard_mode=int(value.hard), toggle=value.toggle)
    if decode(value.name, rows, tables) != expected:
        raise ValueError("Internal password verification failed")
    return rows


def smoke() -> None:
    count = rejected = 0
    assert tuple(value for _, value in COMPANIONS) == (0, 3, 1, 2)
    for stage in range(len(STAGES)):
        for hard in (False, True):
            allowed = choices(stage, hard, EXPECTED)
            for label, partner in COMPANIONS:
                state = Selection("TREVOR", stage, partner, hard)
                if allowed[label]:
                    assert len(password(state, EXPECTED)) == 4
                    count += 1
                else:
                    try:
                        password(state, EXPECTED)
                    except ValueError:
                        rejected += 1
                    else:
                        raise AssertionError("Invalid route/partner allowed")
    assert count == 119 and rejected == 25
    for bad in (Selection("TREVOR", -1, 0),
                Selection("TREVOR", len(STAGES), 0),
                Selection("TREVOR", 0, 4)):
        try:
            password(bad, EXPECTED)
        except ValueError:
            continue
        raise AssertionError("Invalid index allowed")
    print(f"PASS JP stage and companion menu: {count} allowed, {rejected} rejected")


def show(rom: Path | None) -> None:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox

    root = tk.Tk()
    root.title("CVIII JP - Stage and Companion Debug")
    root.geometry("650x490")
    root.resizable(False, False)
    if rom is None:
        path = filedialog.askopenfilename(
            parent=root, title="Choose original Akumajou Densetsu Japanese ROM",
            filetypes=[("NES ROM", "*.nes"), ("All files", "*")])
        if not path:
            root.destroy()
            return
        rom = Path(path)
    try:
        tables = load_tables(rom)
    except (OSError, ValueError) as error:
        messagebox.showerror("Japanese ROM rejected", str(error), parent=root)
        root.destroy()
        return

    frame = ttk.Frame(root, padding=18)
    frame.pack(fill="both", expand=True)
    frame.columnconfigure(1, weight=1)
    vars = [tk.StringVar(value="TREVOR"), tk.StringVar(),
            tk.StringVar(), tk.BooleanVar(value=False), tk.IntVar(value=0)]
    name, stage, companion, hard, toggle = vars
    stages = [f"{i:02d}  {title}" for i, title in enumerate(STAGES)]
    ttk.Label(frame, text="STAGE + COMPANION PASSWORD TEST",
              font=("Segoe UI", 12, "bold")).grid(
                  row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

    def title(row: int, text: str) -> None:
        ttk.Label(frame, text=text).grid(row=row, column=0, sticky="w", pady=6)

    title(1, "Player name")
    ttk.Entry(frame, textvariable=name).grid(row=1, column=1, sticky="ew")
    title(2, "Stage/checkpoint")
    stage_box = ttk.Combobox(frame, textvariable=stage, values=stages,
                             state="readonly", width=52)
    stage_box.grid(row=2, column=1, sticky="ew")
    title(3, "Companion")
    partner_box = ttk.Combobox(frame, textvariable=companion,
                               values=[label for label, _ in COMPANIONS],
                               state="readonly", width=30)
    partner_box.grid(row=3, column=1, sticky="ew")
    title(4, "Game mode")
    ttk.Checkbutton(frame, text="Hard (changes difficulty)",
                    variable=hard).grid(row=4, column=1, sticky="w")
    title(5, "Password variation")
    ttk.Combobox(frame, textvariable=toggle, values=[0, 1],
                 state="readonly", width=5).grid(row=5, column=1, sticky="w")
    ttk.Separator(frame).grid(row=6, column=0, columnspan=2,
                              sticky="ew", pady=(12, 8))
    ttk.Label(frame, text="Password symbols: W=Whip, R=Rosary, H=Heart, .=blank").grid(
        row=7, column=0, columnspan=2, sticky="w")
    grid = tk.StringVar(value="")
    status = tk.StringVar(value="")
    ttk.Label(frame, textvariable=grid, font=("Consolas", 18)).grid(
        row=8, column=0, columnspan=2, sticky="w", pady=10)
    ttk.Label(frame, textvariable=status, wraplength=580).grid(
        row=9, column=0, columnspan=2, sticky="w")

    def selected() -> Selection:
        a, b = stage_box.current(), partner_box.current()
        if a < 0 or b < 0:
            raise ValueError("Choose a stage and a companion")
        return Selection(name.get(), a, COMPANIONS[b][1], hard.get(), toggle.get())

    def refresh(*_args: object) -> None:
        try:
            rows = password(selected(), tables)
        except ValueError as error:
            grid.set("-")
            status.set(str(error))
            copy.state(["disabled"])
            return
        grid.set("\n".join("  ".join(line) for line in rows))
        status.set("Password candidate only. Enter at the game's password screen; "
                   "Japanese game acceptance requires independent confirmation.")
        copy.state(["!disabled"])

    def copy_grid() -> None:
        rows = password(selected(), tables)
        root.clipboard_clear()
        root.clipboard_append("\n".join(" ".join(line) for line in rows))
        root.update()
        status.set("Password grid copied to clipboard.")

    copy = ttk.Button(frame, text="Copy password", command=copy_grid)
    copy.grid(row=10, column=0, sticky="w", pady=12)
    ttk.Button(frame, text="Close", command=root.destroy).grid(
        row=10, column=1, sticky="e", pady=12)
    for field in vars:
        field.trace_add("write", refresh)
    stage_box.current(0)
    partner_box.current(0)
    refresh()
    root.mainloop()


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rom", type=Path, help="Original JP ROM; chooser if omitted")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        smoke()
    else:
        show(a.rom)


if __name__ == "__main__":
    main()
