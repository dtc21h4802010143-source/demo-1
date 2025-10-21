import csv

programs = [
    ["Công nghệ thông tin", "7480201", "Khoa Công nghệ thông tin", "Đào tạo chuyên gia về phát triển phần mềm và hệ thống thông tin", "4 năm", "Tổ hợp A00, A01, D01", "Lập trình viên, Phân tích hệ thống, Quản lý dự án CNTT", "12000000"],
    ["Kỹ thuật phần mềm", "7480103", "Khoa Công nghệ thông tin", "Đào tạo kỹ sư phần mềm chuyên nghiệp", "4 năm", "Tổ hợp A00, A01", "Kỹ sư phần mềm, DevOps, Software Architect", "12000000"],
    ["Khoa học máy tính", "7480101", "Khoa Công nghệ thông tin", "Đào tạo chuyên sâu về thuật toán, AI và khoa học dữ liệu", "4 năm", "Tổ hợp A00, A01", "Data Scientist, AI Engineer, Research Scientist", "13000000"],
    ["An ninh mạng", "7480202", "Khoa Công nghệ thông tin", "Đào tạo chuyên gia bảo mật và an toàn thông tin", "4 năm", "Tổ hợp A00, A01", "Chuyên viên bảo mật, Penetration Tester, Security Analyst", "12500000"],
    ["Kỹ thuật máy tính", "7480106", "Khoa Công nghệ thông tin", "Đào tạo về kiến trúc máy tính và hệ thống nhúng", "4 năm", "Tổ hợp A00, A01", "Kỹ sư phần cứng, Embedded System Developer", "12000000"],
    ["Hệ thống thông tin", "7340405", "Khoa Công nghệ thông tin", "Đào tạo về quản trị và phân tích hệ thống thông tin", "4 năm", "Tổ hợp A00, A01, D01", "Business Analyst, System Administrator, IT Manager", "11500000"],
    ["Mạng máy tính và truyền thông dữ liệu", "7480102", "Khoa Công nghệ thông tin", "Đào tạo về mạng máy tính và truyền thông", "4 năm", "Tổ hợp A00, A01", "Network Engineer, Network Administrator, Telecom Specialist", "12000000"],
    ["Tự động hóa", "7510203", "Khoa Kỹ thuật và Công nghệ", "Đào tạo về điều khiển và tự động hóa công nghiệp", "4 năm", "Tổ hợp A00, A01", "Kỹ sư tự động hóa, PLC Programmer, Control System Engineer", "12000000"],
    ["Cơ điện tử", "7510204", "Khoa Kỹ thuật và Công nghệ", "Đào tạo về robot và hệ thống cơ điện tử thông minh", "4 năm", "Tổ hợp A00, A01", "Kỹ sư robot, Mechatronics Engineer, Automation Engineer", "12500000"],
    ["Công nghệ ô tô", "7510205", "Khoa Kỹ thuật và Công nghệ", "Đào tạo về công nghệ và kỹ thuật ô tô hiện đại", "4 năm", "Tổ hợp A00, A01", "Kỹ sư ô tô, Automotive Engineer, Quality Control", "11500000"],
    ["Điện tử viễn thông", "7520207", "Khoa Kỹ thuật và Công nghệ", "Đào tạo về điện tử và hệ thống viễn thông", "4 năm", "Tổ hợp A00, A01", "Kỹ sư điện tử, Telecom Engineer, RF Engineer", "12000000"],
    ["Kỹ thuật Điện", "7510301", "Khoa Kỹ thuật và Công nghệ", "Đào tạo về hệ thống điện và năng lượng", "4 năm", "Tổ hợp A00, A01", "Kỹ sư điện, Power System Engineer, Electrical Designer", "11500000"],
    ["Điện tử", "7520114", "Khoa Kỹ thuật và Công nghệ", "Đào tạo về thiết kế và chế tạo mạch điện tử", "4 năm", "Tổ hợp A00, A01", "Kỹ sư điện tử, Electronics Designer, PCB Designer", "11500000"],
    ["Vi mạch bán dẫn", "7510302", "Khoa Kỹ thuật và Công nghệ", "Đào tạo về thiết kế và sản xuất vi mạch tích hợp", "4 năm", "Tổ hợp A00, A01", "IC Designer, Chip Engineer, Semiconductor Engineer", "13500000"],
    ["Quản lý logistics và chuỗi cung ứng", "7340602", "Khoa Kinh tế và Quản trị", "Đào tạo về quản lý chuỗi cung ứng và logistics", "4 năm", "Tổ hợp A00, D01, C00", "Logistics Manager, Supply Chain Analyst, Operations Manager", "11000000"],
    ["Thương mại điện tử", "7340122", "Khoa Kinh tế và Quản trị", "Đào tạo về kinh doanh trực tuyến và thương mại điện tử", "4 năm", "Tổ hợp A01, D01, C00", "E-commerce Manager, Digital Marketing, Online Business Owner", "11500000"],
    ["Quản trị kinh doanh số", "7340101", "Khoa Kinh tế và Quản trị", "Đào tạo về quản trị doanh nghiệp trong môi trường số", "4 năm", "Tổ hợp A01, D01, C00", "Business Manager, Digital Transformation Manager, CEO", "11500000"],
    ["Marketing số", "7340115", "Khoa Kinh tế và Quản trị", "Đào tạo về tiếp thị và quảng cáo kỹ thuật số", "4 năm", "Tổ hợp A01, D01, C00", "Digital Marketer, SEO/SEM Specialist, Content Marketing Manager", "11500000"],
    ["Quản trị văn phòng", "7340406", "Khoa Kinh tế và Quản trị", "Đào tạo về quản lý văn phòng và hành chính", "4 năm", "Tổ hợp D01, C00", "Office Manager, Executive Assistant, Administrative Manager", "10500000"],
    ["Công nghệ tài chính", "7340201", "Khoa Kinh tế và Quản trị", "Đào tạo về ứng dụng công nghệ trong tài chính và ngân hàng", "4 năm", "Tổ hợp A00, A01, D01", "Fintech Developer, Financial Analyst, Blockchain Developer", "12500000"],
    ["Hệ thống thông tin kinh tế", "7340123", "Khoa Kinh tế và Quản trị", "Đào tạo về phân tích và quản trị hệ thống thông tin kinh tế", "4 năm", "Tổ hợp A00, A01, D01", "Business Intelligence Analyst, ERP Consultant, IT Business Analyst", "11500000"],
    ["Thiết kế đồ họa", "7210403", "Khoa Nghệ thuật và Truyền thông", "Đào tạo về thiết kế đồ họa và hình ảnh số", "4 năm", "Tổ hợp D01, V00 hoặc có năng khiếu", "Graphic Designer, UI/UX Designer, Art Director", "12000000"],
    ["Công nghệ truyền thông", "7320104", "Khoa Nghệ thuật và Truyền thông", "Đào tạo về công nghệ và kỹ thuật truyền thông hiện đại", "4 năm", "Tổ hợp D01, C00, V00", "Content Creator, Media Producer, Communication Specialist", "11500000"],
    ["Truyền thông đa phương tiện", "7320105", "Khoa Nghệ thuật và Truyền thông", "Đào tạo về sản xuất nội dung đa phương tiện", "4 năm", "Tổ hợp D01, C00, V00", "Multimedia Producer, Video Editor, Motion Graphics Designer", "12000000"],
    ["Nghệ thuật số", "7210407", "Khoa Nghệ thuật và Truyền thông", "Đào tạo về nghệ thuật và sáng tạo kỹ thuật số", "4 năm", "Tổ hợp D01, V00 hoặc có năng khiếu", "Digital Artist, 3D Modeler, Game Designer", "13000000"],
    ["Công nghệ thông tin quốc tế", "7480211", "Khoa Liên kết quốc tế", "Chương trình CNTT chất lượng cao liên kết quốc tế", "4 năm", "Tổ hợp A00, A01, tiếng Anh tốt", "International IT Professional, Global Project Manager", "18000000"],
    ["Kỹ thuật phần mềm liên kết quốc tế", "7480113", "Khoa Liên kết quốc tế", "Chương trình kỹ thuật phần mềm liên kết với đại học nước ngoài", "4 năm", "Tổ hợp A00, A01, tiếng Anh tốt", "Software Engineer (International), Solutions Architect", "18000000"],
    ["Công nghệ thông tin trọng điểm", "7480212", "Khoa Liên kết quốc tế", "Chương trình CNTT chất lượng cao trọng điểm", "4 năm", "Tổ hợp A00, A01, điểm cao", "Senior Developer, Tech Lead, CTO", "16000000"],
    ["Ngôn ngữ Anh", "7220201", "Khoa Ngôn ngữ", "Đào tạo tiếng Anh cho truyền thông và giao tiếp quốc tế", "4 năm", "Tổ hợp D01, D14, D15", "English Teacher, Translator, International Communication Specialist", "10500000"],
]

with open(r'C:\Users\Bạc Cầm Ngọc\ttks\TS2\admission_system\data\programs.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['name', 'code', 'department', 'description', 'duration', 'requirements', 'career_prospects', 'tuition_fee'])
    writer.writerows(programs)

print("✅ Created programs.csv with 29 programs")
