with open(r"c:\Users\AntonioRC\Desktop\PIE\book_extracted.txt", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

# Extract Chapter 7 (lines 6090 to 7200)
ch7_lines = lines[6085:7200]
with open(r"c:\Users\AntonioRC\Desktop\PIE\scratch\chapter7.txt", "w", encoding="utf-8") as f:
    for line in ch7_lines:
        clean = line.replace('\u2005', ' ').replace('\u2013', '-').replace('\u2014', '-').replace('\u201d', '"').replace('\u201c', '"')
        f.write(clean)

# Extract Appendix K (lines 13575 to 13800)
appk_lines = lines[13570:13800]
with open(r"c:\Users\AntonioRC\Desktop\PIE\scratch\appendix_k.txt", "w", encoding="utf-8") as f:
    for line in appk_lines:
        clean = line.replace('\u2005', ' ').replace('\u2013', '-').replace('\u2014', '-').replace('\u201d', '"').replace('\u201c', '"')
        f.write(clean)

print("Extracted Chapter 7 and Appendix K successfully.")
