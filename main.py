"""Generate the animated terminal profile README."""

from datetime import datetime
import os
from pathlib import Path

os.environ.setdefault("GIFOS_GENERAL_USER_NAME", "moosacodes")

import gifos


ROOT = Path(__file__).resolve().parent
FONT_BITMAP = str(ROOT / "fonts" / "gohufont-uni-14.pil")
FONT_LOGO = str(ROOT / "fonts" / "vtks-blocketo.regular.ttf")
FONT_MONA = str(ROOT / "fonts" / "Inversionz.otf")


def main() -> None:
    terminal = gifos.Terminal(750, 600, 15, 15, FONT_BITMAP, 15)
    terminal.gen_text("", 1, count=20)
    terminal.toggle_show_cursor(False)
    year = datetime.now().year

    terminal.gen_text("GIF_OS Modular BIOS v1.0.11", 1)
    terminal.gen_text(
        f"Copyright (C) {year}, \x1b[31mMOOSA//SYS\x1b[0m",
        2,
    )
    terminal.gen_text("\x1b[94mGitHub Profile ReadMe Terminal, Rev 1011\x1b[0m", 4)
    terminal.gen_text("Krypton(tm) GIFCPU - 250Hz", 6)
    terminal.gen_text(
        "Press \x1b[94mDEL\x1b[0m to enter SETUP, \x1b[94mESC\x1b[0m to cancel Memory Test",
        terminal.num_rows,
    )
    for value in range(0, 65653, 7168):
        terminal.delete_row(7)
        terminal.gen_text(
            f"Memory Test: {value}",
            7,
            count=2 if value < 30000 else 1,
            contin=True,
        )
    terminal.delete_row(7)
    terminal.gen_text("Memory Test: 64KB OK", 7, count=10, contin=True)
    terminal.gen_text("", 11, count=10, contin=True)

    terminal.clear_frame()
    terminal.gen_text("Initiating Boot Sequence ", 1, contin=True)
    terminal.gen_typing_text(".....", 1, contin=True)
    terminal.gen_text("\x1b[96m", 1, count=0, contin=True)
    terminal.set_font(FONT_LOGO, 66)
    logo = "MOOSA"
    middle_row = (terminal.num_rows + 1) // 2
    middle_column = (terminal.num_cols - len(logo) + 1) // 2
    effect_lines = gifos.effects.text_scramble_effect_lines(
        logo,
        3,
        include_special=False,
    )
    for line in effect_lines:
        terminal.delete_row(middle_row + 1)
        terminal.gen_text(line, middle_row + 1, middle_column + 1)

    terminal.set_font(FONT_BITMAP, 15)
    terminal.clear_frame()
    terminal.clone_frame(5)
    terminal.toggle_show_cursor(False)
    terminal.gen_text("\x1b[93mGIF OS v1.0.11 (tty1)\x1b[0m", 1, count=5)
    terminal.gen_text("login: ", 3, count=5)
    terminal.toggle_show_cursor(True)
    terminal.gen_typing_text("moosacodes", 3, contin=True)
    terminal.gen_text("", 4, count=5)
    terminal.toggle_show_cursor(False)
    terminal.gen_text("password: ", 4, count=5)
    terminal.toggle_show_cursor(True)
    terminal.gen_typing_text("**********", 4, contin=True)
    terminal.toggle_show_cursor(False)
    terminal.gen_text(
        f"Last login: {datetime.now().strftime('%a %b %d %I:%M:%S %p')} on tty1",
        6,
    )

    terminal.gen_prompt(7, count=5)
    prompt_column = terminal.curr_col
    terminal.toggle_show_cursor(True)
    terminal.gen_typing_text("\x1b[91mclea", 7, contin=True)
    terminal.delete_row(7, prompt_column)
    terminal.gen_text("\x1b[92mclear\x1b[0m", 7, count=3, contin=True)

    github_stats = gifos.utils.fetch_github_stats("moosacodes", [])
    terminal.clear_frame()
    languages = [language[0] for language in github_stats.languages_sorted]
    details = f"""
    \x1b[30;101mmoosacodes@GitHub\x1b[0m
    ------------------
    \x1b[96mOS:     \x1b[93mWindows, Linux\x1b[0m
    \x1b[96mHost:   \x1b[93mUniversity of Guelph\x1b[0m
    \x1b[96mKernel: \x1b[93mComputer Science\x1b[0m
    \x1b[96mIDE:    \x1b[93mVSCode, Neovim\x1b[0m
    \x1b[96mFocus:  \x1b[93mAI infrastructure, HPC, distributed systems\x1b[0m

    \x1b[30;101mProjects:\x1b[0m
    ------------------
    \x1b[96mOpen-Role-Radar\x1b[0m
    \x1b[96mInfraPulse\x1b[0m
    \x1b[96mAgent-Seatbelt\x1b[0m

    \x1b[30;101mGitHub Stats:\x1b[0m
    ------------------
    \x1b[96mUser Rating: \x1b[93m{github_stats.user_rank.level}\x1b[0m
    \x1b[96mTotal Stars Earned: \x1b[93m{github_stats.total_stargazers}\x1b[0m
    \x1b[96mTotal Commits ({year - 1}): \x1b[93m{github_stats.total_commits_last_year}\x1b[0m
    \x1b[96mTotal PRs: \x1b[93m{github_stats.total_pull_requests_made}\x1b[0m
    \x1b[96mMerged PR %: \x1b[93m{github_stats.pull_requests_merge_percentage}\x1b[0m
    \x1b[96mTotal Contributions: \x1b[93m{github_stats.total_repo_contributions}\x1b[0m
    \x1b[96mTop Languages: \x1b[93m{', '.join(languages[:3])}\x1b[0m
    """
    terminal.gen_prompt(1)
    prompt_column = terminal.curr_col
    terminal.clone_frame(10)
    terminal.toggle_show_cursor(True)
    terminal.gen_typing_text("\x1b[91mfetch.s", 1, contin=True)
    terminal.delete_row(1, prompt_column)
    terminal.gen_text("\x1b[92mfetch.sh\x1b[0m", 1, count=3, contin=True)
    terminal.gen_typing_text(" -u moosacodes", 1, contin=True)

    terminal.set_font(FONT_MONA, 16, 0)
    terminal.toggle_show_cursor(False)
    terminal.gen_text(
        r"""
    \x1b[49m     \x1b[90;100m}}\x1b[49m     \x1b[90;100m}}\x1b[0m
    \x1b[49m    \x1b[90;100m}}}}\x1b[49m   \x1b[90;100m}}}}\x1b[0m
    \x1b[49m    \x1b[90;100m}}}}}\x1b[49m \x1b[90;100m}}}}}\x1b[0m
    \x1b[49m   \x1b[90;100m}}}}}}}}}}}}}\x1b[0m
    \x1b[49m   \x1b[90;100m}}}}}}}}}}}}}}\x1b[0m
    \x1b[49m   \x1b[90;100m}}\x1b[37;47m}}}}}}}\x1b[90;100m}}}}}\x1b[0m
    \x1b[49m  \x1b[90;100m}}\x1b[37;47m}}}}}}}}}}\x1b[90;100m}}}\x1b[0m
    \x1b[49m  \x1b[90;100m}}\x1b[37;47m}\x1b[90;100m}\x1b[37;47m}}}}}\x1b[90;100m}\x1b[37;47m}}\x1b[90;100m}}}}\x1b[0m
    \x1b[49m  \x1b[90;100m}\x1b[37;47m}}\x1b[90;100m}\x1b[37;47m}}}}}\x1b[90;100m}\x1b[37;47m}}}\x1b[90;100m}}}\x1b[0m
    \x1b[90;100m}}}\x1b[37;47m}}}}\x1b[90;100m}}}\x1b[37;47m}}}}}\x1b[90;100m}}}}\x1b[0m
    \x1b[49m  \x1b[90;100m}\x1b[37;47m}}}}}\x1b[90;100m}}\x1b[37;47m}}}}}\x1b[90;100m}}}\x1b[0m
    \x1b[49m \x1b[90;100m}}\x1b[37;47m}}}}}}}}}}}}\x1b[90;100m}}}\x1b[0m
    \x1b[90;100m}\x1b[49m  \x1b[90;100m}}\x1b[37;47m}}}}}}}}\x1b[90;100m}}}\x1b[49m  \x1b[90;100m}\x1b[0m
    \x1b[49m        \x1b[90;100m}}}}}\x1b[0m
    \x1b[49m       \x1b[90;100m}}}}}}}\x1b[0m
    \x1b[49m       \x1b[90;100m}}}}}}}}\x1b[0m
    \x1b[49m      \x1b[90;100m}}}}}}}}}}\x1b[0m
    \x1b[49m     \x1b[90;100m}}}}}}}}}}}\x1b[0m
    \x1b[49m     \x1b[90;100m}}}}}}}}}}}}\x1b[0m
    \x1b[49m     \x1b[90;100m}}\x1b[49m \x1b[90;100m}}}}}}\x1b[49m \x1b[90;100m}}\x1b[0m
    \x1b[49m        \x1b[90;100m}}}}}}}\x1b[0m
    \x1b[49m         \x1b[90;100m}}}\x1b[49m \x1b[90;100m}}\x1b[0m
    """,
        10,
    )
    terminal.set_font(FONT_BITMAP)
    terminal.toggle_show_cursor(True)
    terminal.gen_text(details, 2, 35, count=5, contin=True)
    terminal.gen_prompt(terminal.curr_row)
    terminal.gen_typing_text(
        "\x1b[92m# Have a nice day kind stranger :D Thanks for stopping by!",
        terminal.curr_row,
        contin=True,
    )
    terminal.gen_text("", terminal.curr_row, count=120, contin=True)
    terminal.gen_gif()

    readme = f"""<div align="justify">
<picture>
    <source media="(prefers-color-scheme: dark)" srcset="./output.gif">
    <source media="(prefers-color-scheme: light)" srcset="./output.gif">
    <img alt="Moosa Alam's animated terminal profile" src="output.gif">
</picture>
</div>
"""
    (ROOT / "README.md").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
