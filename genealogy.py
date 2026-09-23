#!/usr/bin/env python3
"""
Python translation of the supplied C++ genealogy/HTML generator.

The C++ field/MyString classes have been replaced with ordinary Python str
objects.  Input records are pipe-separated and contain 14 fields:

0  num
1  hnum
2  first name
3  last name
4  where born
5  birth date
6  death date
7  spouse term
8  marriage date
9  spouse
10 spouse where born
11 spouse birth date
12 spouse death date
13 spouse link
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import html
import sys


HTML_FILE = "{}.htm"
HTML_LINK_PARENT = "../{}"
HTML_FILE_CHLD = "{}c.htm"
HTML_FILE_PIC = "{}p.htm"
HTML_FILE_HIST = "{}h.htm"
HTML_FILE_STORY = "{}s.htm"

UNIQUE_NUMBER = 0


def print_html_head(fp, title="HTML Page"):
    fp.write(
        f"<html>\n<head>\n<title>{title}</title>\n"
        f"<p align=center> <H1>\n{title}</H1>\n"
        f"<body bgcolor=white>\n"
    )


def print_html_end(fp):
    fp.write("</body>\n</html>\n")


def print_href(fp, txt, ref, add_space=True):
    # Preserve the original output convention: references are supplied
    # without .htm and the generated link gets .htm appended.
    space = " " if add_space else ""
    fp.write(f"<a href={ref}.htm>{space}{txt}</a>")


def print_blue(fp, txt, size=None):
    if size is None:
        fp.write(f"<font color=blue>{txt}</font> ")
    else:
        fp.write(f'<font color=blue size=+{size}>{txt}</font> ')


def print_bold(fp, txt):
    fp.write(f"<b>{txt}</b>")


@dataclass
class Name:
    first_name: str = ""
    last_name: str = ""

    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def set_name(self, first_name: str, last_name: str):
        self.first_name = first_name
        self.last_name = last_name


@dataclass
class Vitals:
    num: int = 0
    generation: int = 0
    children: int = 0
    hnum: str = ""
    fname: str = ""
    lname: str = ""
    spouse_term: str = ""
    spouse: str = ""
    spouse_link: str = ""
    html_page: str = ""
    dad_name: str = ""
    dad_link: str = ""
    mom_name: str = ""
    mom_link: str = ""

    def set_person(
        self,
        hnum: str,
        num: int,
        generation: int,
        fname: str,
        lname: str,
        spouse_term: str,
        spouse: str,
        spouse_link: str,
        mom_name: str = "",
        mom_link: str = "",
        dad_name: str = "",
        dad_link: str = "",
        unique: str = "X",
    ):
        self.hnum = hnum
        self.num = num
        self.generation = generation
        self.fname = fname
        self.lname = lname
        self.spouse_term = spouse_term
        self.spouse = spouse
        self.spouse_link = spouse_link
        self.mom_name = mom_name
        self.mom_link = mom_link
        self.dad_name = dad_name
        self.dad_link = dad_link
        self.html_page = f"{unique}{lname[:5]}/{num}"

    def full_name(self) -> str:
        return f"{self.fname} {self.lname}"

    def last_comma_first(self) -> str:
        return f"{self.lname}, {self.fname}"

    def hnum_parent(self) -> str:
        return self.hnum.rsplit("-", 1)[0] if "-" in self.hnum else self.hnum

    def increment_children(self):
        self.children += 1


@dataclass
class Person(Vitals):
    where_born: str = ""
    bdate: str = ""
    ddate: str = ""
    mdate: str = ""
    s_where_born: str = ""
    sbdate: str = ""
    sddate: str = ""

    def set_person(
        self,
        hnum: str,
        num: int,
        generation: int,
        fname: str,
        lname: str,
        where_born: str,
        bdate: str,
        ddate: str,
        spouse_term: str,
        mdate: str,
        spouse: str,
        s_where_born: str,
        sbdate: str,
        sddate: str,
        spouse_link: str,
        unique: str = "X",
    ):
        super().set_person(
            hnum, num, generation, fname, lname,
            spouse_term, spouse, spouse_link, unique=unique
        )
        self.where_born = where_born
        self.bdate = bdate
        self.ddate = ddate
        self.mdate = mdate
        self.s_where_born = s_where_born
        self.sbdate = sbdate
        self.sddate = sddate

    def page(self, parents: "Vitals | None" = None, output_dir: Path = Path(".")):
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = output_dir / HTML_FILE.format(self.html_page)
        filename.parent.mkdir(parents=True, exist_ok=True)
        if parents is None:
            with filename.open("w", encoding="utf-8") as fp:
                self._html_info1(fp, output_dir)
                self._html_info2(fp)
            return

        with filename.open("w", encoding="utf-8") as fp:
            self._html_info1(fp, output_dir)

            lname = self.lname.upper()
            lname_parents = parents.lname.upper()
            link = HTML_LINK_PARENT.format(parents.html_page)
            parent_filename = output_dir / HTML_FILE.format(parents.html_page)

            if lname == lname_parents:
                self.mom_name = parents.spouse
                self.mom_link = parents.spouse_link
                self.dad_name = parents.full_name()
                self.dad_link = link
            else:
                self.dad_name = parents.spouse
                self.dad_link = parents.spouse_link
                self.mom_name = parents.full_name()
                self.mom_link = link

            fp.write("<br>\n")
            print_bold(fp, "Mother: ")
            if self.mom_link:
                print_href(fp, self.mom_name, self.mom_link)
            else:
                print_blue(fp, self.mom_name)

            print_bold(fp, " Father: ")
            if self.dad_link:
                print_href(fp, self.dad_name, self.dad_link)
            else:
                print_blue(fp, self.dad_name)
            fp.write("\n")

            self._html_info2(fp)

        parents.increment_children()
        self.add_children(parents, parent_filename, output_dir)

        if parents.spouse_link:
            # The C++ code removes the first three characters from the spouse link.
            spouse_child_file = output_dir / HTML_FILE_CHLD.format(
                parents.spouse_link[3:]
            )
            self.add_children(parents, spouse_child_file, output_dir)

    def add_children(
        self, parents: Vitals, filename: Path, output_dir: Path = Path(".")
    ):
        filename.parent.mkdir(parents=True, exist_ok=True)

        first_marriage = bool(
            self.hnum
            and (self.hnum[-1] in {"a", "S", "?"} or self.hnum[-1].isdigit())
        )

        with filename.open("a", encoding="utf-8") as fp:
            if parents.children == 1:
                fp.write("<p>")
                print_bold(fp, "Children: ")
                fp.write("<ol>\n<li>")
            elif first_marriage:
                fp.write("<br><li>")
            else:
                fp.write("<br>")

            link = HTML_LINK_PARENT.format(self.html_page)
            print_href(fp, self.full_name(), link)

            if self.bdate:
                fp.write(f'\n      - Born <b>{self.bdate}</b>.')
            if self.spouse:
                fp.write(
                    f'\n      {self.spouse_term} <b>{self.spouse}</b>.'
                )
            fp.write("\n")

    def html_children(self, output_dir: Path = Path(".")):
        filename = output_dir / HTML_FILE.format(self.html_page)
        child_filename = output_dir / HTML_FILE_CHLD.format(self.html_page)

        if not filename.exists():
            print(f"Unable to write HTML page: {filename}")
            return

        if child_filename.exists():
            self.children += 1
            with child_filename.open("r", encoding="utf-8") as child_fp:
                with filename.open("a", encoding="utf-8") as out_fp:
                    for line in child_fp:
                        out_fp.write(line)
            child_filename.unlink()

        with filename.open("a", encoding="utf-8") as fp:
            if self.children > 0:
                fp.write("</ol>\n")

    def html_done(self, output_dir: Path = Path(".")):
        filename = output_dir / HTML_FILE.format(self.html_page)
        with filename.open("a", encoding="utf-8") as fp:
            print_html_end(fp)

    def _html_info1(self, fp, output_dir):
        fp.write(
            '<html><body bgcolor=white>\n'
            '<HR>\n <p align=center><font size=+3>'
        )
        print_bold(fp, self.lname)
        print_bold(fp, " Genealogy")
        fp.write(
            '</font>\n'
            '\n <br> '
            '<a href=../index.htm >Names</a>\n'
            '<a href=../dobindex.htm >Birthdays</a>\n'
            '<a href=../genindex.htm >Generations</a>\n'
            '\n <br> '
            '<a href=../hisindex.htm >Histories</a>\n'
            '<a href=../stoindex.htm >Stories</a>\n'
            '<a href=../picindex.htm >Pictures</a></p>\n'
            '<table width=100% border=0cellpadding=0 cellspacing=1>\n'
            '<tr>\n'
            '<td width=40% align=left rowspan=1>\n'
        )
        print_blue(fp, self.full_name(), 2)
        fp.write(
            '</td>\n'
            '<td width=20% align=left rowspan=1>\n'
            f' Generation {self.generation}'
            '</td>\n'
            '<td width=10% align=center rowspan=1>\n'
        )

        if (output_dir / HTML_FILE_HIST.format(self.html_page)).exists():
            fp.write(f"<a href={self.num}h.htm>History</a>\n")

        fp.write(
            '</td>\n<td width=10% align=center rowspan=1>\n'
        )
        if (output_dir / HTML_FILE_STORY.format(self.html_page)).exists():
            fp.write(
                f'<a href={self.num}s.htm><img alt=STORIES '
                f'src="../mysyms/stories.gif" align=center border=0></a>\n'
            )

        fp.write(
            '</td>\n<td width=10% align=center rowspan=1>\n'
        )
        if (output_dir / HTML_FILE_PIC.format(self.html_page)).exists():
            fp.write(
                f'<a href={self.num}p.htm><img alt=PICTURES '
                f'src="../mysyms/pics.gif" align=center border=0></a>\n'
            )

        fp.write(
            '</td>\n<td width=10% align=center rowspan=1>\n'
            '</td>\n</tr>\n</table>\n<br>'
        )

        print_bold(fp, "Birth: ")
        fp.write(self.bdate if self.bdate else "UNKNOWN")

        print_bold(fp, " Place: ")
        fp.write((self.where_born if self.where_born else "UNKNOWN") + "\n")

        if self.ddate:
            fp.write("<br>")
            print_bold(fp, "Death: ")
            fp.write(self.ddate + "\n")

        fp.write("<br>\n")

    def _html_info2(self, fp):
        if self.spouse:
            fp.write("<p>")
            fp.write(f"<b> {self.spouse_term}</b>: ")
            fp.write(self.mdate + " ")
            if self.spouse_link:
                print_href(fp, self.spouse, self.spouse_link)
            else:
                print_blue(fp, self.spouse)

            if self.sbdate:
                fp.write(f" ({self.sbdate} - {self.sddate})\n")

    def index(self, option=None):
        if option == "-d":
            return self.indexby_dob()
        if option == "-g":
            return self.indexby_generation()
        return self.indexby_name()

    def indexby_name(self):
        # C++ indexes are written to stdout, so this function returns the HTML
        # text rather than printing it directly.  main() writes it to stdout.
        out = []
        letter = self.lname[0].upper() if self.lname else ""
        out.append(
            f'<a name = {letter}><p><font size=+4> <b> '
            f'{letter}</font></b></a>\n'
        )
        out.append('<p><font size=+1>')
        out.append(href_text(self.last_comma_first(), self.html_page))
        out.append("</font> - born ")

        out.append(f"<b>{self.bdate}</b>" if self.bdate else "?")
        out.append(f", {self.where_born}." if self.where_born else ".")

        if self.spouse:
            out.append(f"{self.spouse_term} ")
            if self.spouse_link:
                out.append(href_text(self.spouse, self.spouse_link[3:]))
            else:
                out.append(blue_text(self.spouse, 1))
        out.append("\n")
        return "".join(out)

    def indexby_dob(self):
        year_or_date = self.bdate.rsplit("/", 1)[-1] if self.bdate else ""
        out = ["<p> "]
        out.append(f"<b> {year_or_date}</b>" if self.bdate else " ?")
        out.append(" <font size=+1>")
        out.append(href_text(self.last_comma_first(), self.html_page))
        out.append("</font> - born ")
        out.append(f"<b>{self.bdate}</b>" if self.bdate else "?")
        out.append(f", {self.where_born}." if self.where_born else ".")

        if self.spouse:
            out.append(f"{self.spouse_term} ")
            if self.spouse_link:
                out.append(href_text(self.spouse, self.spouse_link[3:]))
            else:
                out.append(blue_text(self.spouse, 1))
        out.append("\n")
        return "".join(out)

    def indexby_generation(self):
        out = [f"<p > {self.generation}", '<font size=+1>']
        out.append(href_text(self.last_comma_first(), self.html_page))
        out.append("</font> - born ")
        out.append(f"<b>{self.bdate}</b>" if self.bdate else "?")
        out.append(f", {self.where_born}." if self.where_born else ".")

        if self.spouse:
            out.append(f"{self.spouse_term} ")
            if self.spouse_link:
                out.append(href_text(self.spouse, self.spouse_link[3:]))
            else:
                out.append(blue_text(self.spouse, 1))
        out.append("\n")
        return "".join(out)

    def generate_tree(self, ngens, html_filename, output_dir=Path(".")):
        filename = output_dir / HTML_FILE.format(html_filename)
        with filename.open("a", encoding="utf-8") as fp:
            mname = self.mom_name
            mlink = self.mom_link
            dname = self.dad_name
            dlink = self.dad_link
            indent_level = ngens - self.generation
            spaces = "    "

            if indent_level == 0:
                fp.write("<p>")
                print_bold(fp, "Family Tree: ")
                fp.write("<pre>")
                fp.write(f"Gen {self.generation} ")
                fp.write(
                    f"<font color=blue><b>{self.full_name()}</b></font>"
                    " - "
                )
                if self.spouse_link:
                    print_href(fp, self.spouse, self.spouse_link, False)
                    fp.write("\n")
                else:
                    print_blue(fp, self.spouse)
                    fp.write("\n")

            if dname:
                fp.write(spaces * indent_level)
                fp.write("      ")

                len_center = max(len(dname), len(self.full_name()))
                fp.write(" " * (len_center // 2))
                fp.write("|\n")

                fp.write(spaces * (indent_level + 1))
                fp.write(f"Gen {self.generation - 1} ")
                if dlink:
                    print_href(fp, dname, dlink, False)
                else:
                    print_blue(fp, dname)
                fp.write(" - ")
            else:
                fp.write("</pre>\n")
                return

            if mname:
                if mlink:
                    print_href(fp, mname, mlink, False)
                    fp.write("\n")
                else:
                    print_blue(fp, mname)
                    fp.write("\n")


def href_text(txt, ref, add_space=True):
    space = " " if add_space else ""
    return f"<a href={ref}.htm>{space}{txt}</a>"


def blue_text(txt, size=None):
    if size is None:
        return f"<font color=blue>{txt}</font> "
    return f'<font color=blue size=+{size}>{txt}</font> '


def parse_person(line: str, unique: str = "X") -> Person:
    # The supplied sample is pipe-separated.  Keep empty fields intact.
    fields = line.rstrip("\r\n").split("|")
    if len(fields) < 14:
        fields += [""] * (14 - len(fields))

    # Do not silently discard extra columns: preserve the first 14 because
    # those are the fields consumed by the original C++ extractor.
    fields = fields[:14]

    raw_num = fields[0].strip()
    num = int(raw_num) if raw_num.isdigit() else 0

    hnum = fields[1]
    generation = hnum.count("-") + 1

    global UNIQUE_NUMBER
    if num == 0:
        UNIQUE_NUMBER += 1
        num = UNIQUE_NUMBER

    person = Person()
    person.set_person(
        hnum=hnum,
        num=num,
        generation=generation,
        fname=fields[2],
        lname=fields[3],
        where_born=fields[4],
        bdate=fields[5],
        ddate=fields[6],
        spouse_term=fields[7],
        mdate=fields[8],
        spouse=fields[9],
        s_where_born=fields[10],
        sbdate=fields[11],
        sddate=fields[12],
        spouse_link=fields[13],
        unique=unique,
    )
    return person


def read_people(datafile, unique="X", max_entries=None):
    people = []
    with open(datafile, "r", encoding="utf-8", errors="replace") as fp:
        for line_number, line in enumerate(fp, 1):
            if not line.strip():
                continue
            if max_entries is not None and len(people) >= max_entries - 1:
                raise RuntimeError(
                    f"Not enough space in array (limit {max_entries})."
                )
            people.append(parse_person(line, unique))
    return people


def write_newdata(people, filename="newdata.txt"):
    # The C++ program writes tab-separated output despite reading pipe-separated
    # fields.  This translation keeps that output behavior for compatibility.
    with open(filename, "w", encoding="utf-8") as fp:
        for p in people:
            fp.write(
                "\t".join([
                    str(p.num), p.hnum, p.fname, p.lname, p.where_born,
                    p.bdate, p.ddate, p.mdate, p.spouse, p.s_where_born,
                    p.sbdate, p.sddate, p.spouse_link
                ]) + "\n"
            )


def find_hnum(hnum_to_find, people):
    if not hnum_to_find:
        return None
    for person in people:
        if person.hnum == hnum_to_find:
            return person
    return None


def run_htmlbldr(
    datafile="sorted.txt",
    unique="X",
    option=None,
    output_dir=".",
    newdatafile="newdata.txt",
    max_entries=400,
):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    people = read_people(datafile, unique, max_entries)
    write_newdata(people, output_dir / newdatafile)

    # Generate index output in the same directory as the original program's
    # stdout-generated index stream.
    index_name = {
        None: "index.htm",
        "-d": "dobindex.htm",
        "-g": "genindex.htm",
    }.get(option, "index.htm")

    index_path = output_dir / index_name
    with index_path.open("w", encoding="utf-8") as index_fp:
        if option is None:
            # Name index starts a section for each encountered last-name letter.
            last_letter = None
            for p in people:
                letter = p.lname[:1].upper() if p.lname else ""
                if letter != last_letter:
                    index_fp.write(
                        f'<a name = {letter}><p><font size=+4> <b> '
                        f'{letter}</font></b></a>\n'
                    )
                    last_letter = letter
                # Avoid the duplicate letter header from indexby_name().
                line = p.indexby_name()
                marker = f'<a name = {letter}><p><font size=+4> <b> {letter}</font></b></a>\n'
                if line.startswith(marker):
                    line = line[len(marker):]
                index_fp.write(line)
        else:
            for p in people:
                index_fp.write(p.index(option))

    # Page generation is order-sensitive, matching the C++ implementation.
    for p in people:
        parent = find_hnum(p.hnum_parent(), people)
        if parent is not None:
            p.page(parent, output_dir)
        else:
            p.page(None, output_dir)

    for p in people:
        p.html_children(output_dir)

    # The original C++ htmlbldr generates a family-tree section for each
    # person, walking from that person up through every available ancestor.
    # Keep the same order: children are finalized first, trees are added next,
    # and the closing HTML is written last.
    for child in people:
        me_hnum = child.hnum
        ngens = child.generation
        while me_hnum:
            ancestor = find_hnum(me_hnum, people)
            if ancestor is not None:
                ancestor.generate_tree(ngens, child.html_page, output_dir)

            if "-" not in me_hnum:
                break
            me_hnum = me_hnum.rsplit("-", 1)[0]

    for p in people:
        p.html_done(output_dir)

    return people


def run_htmlturbo(
    datafile="sorted.txt",
    unique="X",
    option=None,
    output_dir=".",
    newdatafile="newdata.txt",
    max_entries=325,
):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    people = read_people(datafile, unique, max_entries)
    write_newdata(people, output_dir / newdatafile)

    if option is None:
        for p in people:
            print(p.index())
    else:
        for p in people:
            print(p.index(option))

    for p in people:
        parent = find_hnum(p.hnum_parent(), people)
        if parent is not None:
            p.page(parent, output_dir)
        else:
            p.page(None, output_dir)

    for p in people:
        p.html_done(output_dir)

    for p in people:
        print(f"Generate tree for: {p.full_name()}")
        print(f"\tmom is {p.mom_name}, dad is {p.dad_name}")
        print(f"\tmom Link is {p.mom_link}, dad Link is {p.dad_link}")

    return people
