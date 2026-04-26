# Điểm cần Phân tích Sâu cho các Giai đoạn Sau (Future Deep-Dives)

Dựa trên các tài liệu ý tưởng hiện tại, đây là 12 điểm cốt lõi cần được bóc tách và thiết kế chi tiết hơn trong các giai đoạn phát triển tiếp theo.

## 1. Nhóm Kỹ thuật & Kiến trúc (Technical)

1. **Chiến lược Quản lý Context Window nâng cao:**
    * Thiết kế thuật toán **Summary Buffering**: Làm sao để tóm tắt lịch sử mà không làm mất đi những "vibe" tinh tế trong cảm xúc của người dùng.
    * Lồng ghép **RAG (Retrieval-Augmented Generation)**: Khi nào cần "truy xuất" lại ký ức cũ (từ vài tháng trước) thay vì chỉ dùng context hiện tại.
2. **Thiết kế Schema `UserGraph`:**
    * Xây dựng cấu trúc dữ liệu cho thực thể: con người, vật nuôi, sở thích, sự kiện quan trọng.
    * Xử lý cập nhật thông tin: Làm sao để AI biết người dùng đã đổi việc hoặc đã chia tay người yêu để cập nhật vibe hội thoại.
3. **Benchmarking & Model Selection:**
    * Đánh giá thực tế các dòng SLM (Qwen, Llama 3, Mistral) về khả năng **Vibe-matching** và **Instruction Following** trong môi trường tiếng Việt-Anh.
    * Tối ưu hóa độ trễ (Latency) cho trải nghiệm thời gian thực (< 1.5s).

## 2. Nhóm Phương pháp luận & Giáo dục (Learning)

1. **Thuật toán Implicit Feedback:**
    * Xác định tần suất sửa lỗi: Bao nhiêu câu thì nên có một lần lồng ghép cấu trúc đúng để không gây cảm giác "bị dạy bảo".
    * Logic chọn lọc lỗi: Analyst Agent nên ưu tiên sửa lỗi ngữ pháp căn bản hay lỗi dùng từ (word choice)?
2. **Công thức tính Fluency Score:**
    * Xây dựng bộ trọng số cho các chỉ số: AWC (Độ dài câu), Response Momentum (Tốc độ phản hồi), Vocabulary Breadth (Độ rộng từ vựng).
    * Đảm bảo điểm số phản ánh đúng sự tiến bộ thực tế thay vì chỉ đếm số tin nhắn.

## 3. Nhóm Chiến lược & Vận hành (Strategic)

1. **Chiến lược Tối ưu Chi phí (Token Governance):**
    * Xác định ngưỡng (Threshold) cụ thể để chuyển đổi giữa SLM (Buddy) và LLM (Analyst).
    * Cách thức cache context hội thoại để giảm thiểu việc gọi API dư thừa.
2. **Hệ thống Adaptive Re-entry Triggers:**
    * Xây dựng kho nội dung mồi (Priming contents) dựa trên dữ liệu quá khứ của người dùng.
    * Quy tắc thông báo (Notification Policy): Giờ giấc nào là tinh tế nhất để gửi một lời hỏi thăm "Update cuộc sống".
3. **Cơ chế Gamification "Ẩn":**
    * Làm sao để người dùng cảm thấy có "Stakes" (cái giá phải trả) trong các kịch bản Conflict-driven mà không gây stress quá mức.
4. **Cơ chế Nâng cấp Kịch tính (Dynamic Escalation):**
    * Thiết kế logic để Buddy Agent chủ động tăng độ khó hoặc tính kịch tính của tình huống hội thoại dựa trên nỗ lực của người dùng.

## 4. Nhóm Trải nghiệm & Giao diện (UX/UI)

1. **Thiết kế Evidence Archive (Recap UI):**
    * Làm sao để trình bày lỗi sai một cách tích cực (Gamified Grammar).
    * Visual hóa sự tiến bộ để người dùng có thể chia sẻ (Shareability) lên mạng xã hội.
2. **Giám sát Tính nhất quán của Persona:**
    * Làm sao để Buddy Agent không bị "drift" (lệch tính cách) sau một thời gian dài hội thoại hoặc khi context quá lớn.
3. **Safe Zone & Privacy:**
    * Đảm bảo dữ liệu cá nhân trong `UserGraph` được bảo mật tuyệt đối, mang lại cảm giác an tâm hoàn toàn khi người dùng chia sẻ chuyện thầm kín.

---
*Các điểm này sẽ là đầu vào cho quá trình thiết kế PRD chi tiết và các Epic kỹ thuật sau này.*
