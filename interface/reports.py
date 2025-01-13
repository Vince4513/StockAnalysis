from fpdf import FPDF

# ==================================================================================================================================================
# PDF Class
# ==================================================================================================================================================

class PDF(FPDF):
    def header(self, title: str) -> None:
        """Create a proper header

        Args:
            title (str): Title to print in the header
        """
        # Logo
        self.image(r'.\images.png', x = 10, y = 8, w = 30)
        
        # Font
        self.set_font('helvetica', 'B', 20)

        # Calculate width of title and position
        title_w = self.get_string_width(title) + 6
        doc_w = self.w
        self.set_x((doc_w - title_w) / 2)
        
        # Colors of frame, background and text
        self.set_draw_color(0, 0, 0) # border
        self.set_fill_color(170, 170, 170) # background
        self.set_text_color(0, 0, 0) # text
        
        # Thickness of frame (border)
        self.set_line_width(0.5)

        # Title
        self.cell(title_w, 10, title, border = True, ln = True, align='C', fill=True)

        # Line break
        self.ln(10)
    # End def header
    
    def chapter_title(self, ch_num: int, ch_title: str) -> None:
        """Create the chapter title layout

        Args:
            ch_num (int): Chapter number
            ch_title (str): Chapter title 
        """
        self.set_font('helvetica', '', 12)
        self.set_fill_color(200, 200, 255)

        chapter_title = f'Chapter {ch_num}: {ch_title}'
        self.cell(0, 5, chapter_title, ln=True, fill=True)
        self.ln()
    # End def chapter_title

    def chapter_body(self, name: str) -> None:
        """Create the chapter body layout from a txt file

        Args:
            name (str): name of the txt file
        """
        # read text file
        with open(name, 'rb') as fh:
            txt = fh.read().decode('latin-1')
        
        self.set_font('helvetica', '', 10)
        self.multi_cell(0, 5, txt)
        self.ln()
        self.set_font('helvetica', 'I', 10)
        self.cell(0, 5, 'End of chapter')
    # End def chapter_body

    def print_chapter(self, ch_num: int, ch_title: str, name: str) -> None:
        """Display a chapter on a new page in the current pdf

        Args:
            ch_num (int): chpater number
            ch_title (str): chapter title
            name (str): txt file name 
        """
        self.add_page()
        self.chapter_title(ch_num, ch_title)
        self.chapter_body(name)
    # End def print_chapter

    def footer(self) -> None:
        """Create a proper footer in the pdf"""
        
        # Set position of the footer
        self.set_y(-15)
        # Set font
        self.set_font('helvetica', 'I', 10)
        # Set font color grey
        self.set_text_color(169, 169, 169)
        # Page number
        self.cell(0, 10 , f'Page {self.page_no()} / {{nb}}', align='C')
    # End def footer
# End class PDF
