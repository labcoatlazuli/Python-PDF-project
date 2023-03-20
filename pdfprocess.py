from PyPDF2 import PdfFileReader, PdfFileWriter
import copy
import math
import os.path  as path

class OddPagesException(Exception):
    pass

def split_pages(src_path: str, dst_path: str) -> None:
    
    with open(src_path, 'r+b') as src_file, open(dst_path, 'w+b') as dst_file:
        
        reader = PdfFileReader(src_file)
        writer = PdfFileWriter(dst_file)
        pages_first_half, pages_second_half = [], []
        num_pages = reader.getNumPages()

        
        
        if num_pages % 2 != 0:
            raise OddPagesException

        for i in range(num_pages):
            
            first_page = reader.getPage(i)
            second_page = copy.copy(first_page)
            second_page.cropBox = copy.copy(first_page.cropBox)
            
            # get coordinates of 
            x_lowerleft, y_lowerleft = first_page.cropbox.lower_left
            x_upperright, y_upperight = first_page.cropbox.upper_right

            #work out middle x coordinates

            x_middle = (x_lowerleft + x_upperright) / 2
            
            firstpage_middle_upperright_coords = (x_middle, y_upperight)
            secondpage_middle_lowerleft_coords = (x_middle, y_lowerleft)

            # Change page's upper right and copy_page --> this makes two A4s from 1 A3
            first_page.cropbox.upper_right = firstpage_middle_upperright_coords
            second_page.cropbox.lower_left = secondpage_middle_lowerleft_coords

            if i % 2 == 0: # even A3 page index i
                pages_second_half.append(first_page)
                pages_first_half.append(second_page)
            else:
                pages_first_half.append(first_page)
                pages_second_half.append(second_page)


        for page in pages_first_half:
            writer.add_page(page)
        for page in reversed(pages_second_half):
            writer.add_page(page)



        writer.write(dst_file)






            
            

# page[0] --> (n, 0)
# page[1] --> (1, n-1)
# page[2] --> (n-2, 2)
# page[3] --> (3, n-3)
# 
# second_half[n, n-1, n-2, n-3]
# first_half[0, 1, 2, 3]
# 
# 
# even page indices k --> (n-k, k)
# odd page indices k --> (k, n-k)
# 
#         
#         
#         writer.write(dst_file)
# 
# 
# from PyPDF2 import PdfWriter, PdfReader
# 
# reader = PdfReader("example.pdf")
# writer = PdfWriter()
# 
# # add page 1 from reader to output document, unchanged:
# writer.add_page(reader.pages[0])
# writer.add_page()
# 
# # add page 2 from reader, but rotated clockwise 90 degrees:
# writer.add_page(reader.pages[1].rotate(90))
# 
# # add page 3 from reader, but crop it to half size:
# page3 = reader.pages[2]
# page3.cropbox.upper_right = (
#     page3.cropbox.right / 2,
#     page3.cropbox.top / 2,
# )
# writer.add_page(page3)
# 
# # add some Javascript to launch the print window on opening this PDF.
# # the password dialog may prevent the print dialog from being shown,
# # comment the the encription lines, if that's the case, to try this out:
# writer.add_js("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")
# 
# # write to document-output.pdf
# with open("PyPDF2-output.pdf", "wb") as fp:
#     writer.write(fp)