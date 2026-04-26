# NudgeEn: Tầm Nhìn & Mô Tả Ý Tưởng Sản Phẩm

## 1. Tổng quan Dự án (Project Overview)

**NudgeEn** là một nền tảng luyện tiếng Anh thông qua giao tiếp thực tế với AI, được thiết kế để mang lại trải nghiệm như đang trò chuyện với một "người bạn gia sư" thông qua một giao diện nhắn tin hiện đại. Thay vì theo đuổi các lộ trình học thuật khô khan, NudgeEn tập trung vào việc biến việc sử dụng tiếng Anh thành một thói quen hàng ngày tự nhiên và thú vị.

## 2. Giá trị Cốt lõi (Core Value Proposition)

* **Giải trí là "Mồi nhử", Kết quả là "Phần thưởng":** Sự kết nối cảm xúc (Emotional Bonding) là cái "móc" để người dùng mở app mỗi ngày, trong khi các kết quả học tập thực tế (Tangible Results) là giá trị lõi giữ chân họ lâu dài.
* **Học thông qua Thực tế (Real-world Practice):** Chat không theo giáo trình. Hệ thống tự nhiên dẫn dắt người dùng vào các tình huống thực tế (Scenario-based) để rèn luyện phản xạ sinh tồn trong ngôn ngữ.
* **Trải nghiệm Messenger-style:** Giao diện tối ưu cho việc nhắn tin nhanh, mượt mà, giúp người dùng tận dụng rành mạch 5-10 phút rảnh rỗi.
* **Người bạn AI Chủ động (Proactive Companion):** AI không chỉ đợi câu hỏi. Hệ thống **Adaptive Re-entry** xóa bỏ áp lực "tội lỗi" khi user quay lại, biến việc học thành một cuộc hội thoại tự nhiên giữa những người bạn.
* **Học từ Sai lầm (Shadow Learning):** Sửa lỗi tinh tế, không làm ngắt quãng mạch cảm xúc nhưng vẫn đảm bảo tiến bộ học thuật rõ rệt.

## 3. Đối tượng Người dùng Mục tiêu (Target Audience)

* **Level:** Người học đã có vốn từ vựng cơ bản (Basic/Pre-intermediate).
* **Nỗi đau (Pain Point):** "Biết nhưng không dám viết", sợ sai, hoặc thấy học tiếng Anh là một gánh nặng.
* **Triết lý:** "Học mà không biết mình đang học" (Learning without Pressure).

## 4. Các Đặc tính Sản phẩm (Key Product Characteristics)

### A. Kiến trúc "Dual-Agent" (Bộ não kép)

* **Buddy Agent (Interaction):** Chat trực tiếp, tạo vibe, giữ nhiệt hội thoại. Tập trung vào tính cách, cảm xúc và tốc độ phản hồi (Real-time).
* **Analyst Agent (Shadow):** Âm thầm soi lỗi, phân tích sự tiến bộ và chuẩn bị các bản Recap sâu sắc. Đảm bảo tính chính xác học thuật mà không làm phiền mạch chat.
* **Single Story Chat:** Trải nghiệm nhắn tin không biên giới, không chia session, duy trì một mạch lôi cuốn duy nhất như trò chuyện với người thật.

> Xem chi tiết tại [Technical Strategy](technical_strategy.md) về hạ tầng kỹ thuật.

### B. Hành vi & Gắn kết

* **Adaptive Re-entry:** AI nhắn tin hỏi thăm dựa trên bối cảnh cũ (ví dụ: "Buổi phỏng vấn hôm qua của bạn thế nào?"), giúp user quay lại app một cách tự nhiên.
* **Vibe-matching:** Tinh tế trong việc chọn tông giọng. Nếu user đang buồn, AI sẽ không dùng "vibe" hài hước quá đà.
* **Implicit Feedback (Dạy ngầm):** AI thỉnh thoảng sử dụng lại đúng cấu trúc mà user vừa nói sai trong câu trả lời tiếp theo của nó, giúp user học một cách tự nhiên nhất.

> Xem chi tiết tại [Learning Methodology](learning_methodology.md) về các kỹ thuật giáo dục.

### C. Shadow Learning & Tangible Results

* **Immersion Flow:** Ưu tiên 100% sự liền mạch. "Chat trước, Học sau".
* **The Evidence Archive (Bằng chứng tiến bộ):** Cuối mỗi tuần, gửi cho user một bản recap: "Bạn đã dùng được 50 từ mới và xử lý thành công một tình huống khó bằng tiếng Anh".
* **Fluency Score:** Cụ thể hóa sự tiến bộ qua các chỉ số: lượng từ vựng, độ dài câu, và tốc độ phản hồi thay vì chỉ chấm đúng/sai.

## 5. Tại sao NudgeEn khác biệt?

So với các app như Duolingo (lộ trình cứng) hay Tandem (áp lực xã hội), NudgeEn là giải pháp trung hòa:

1. **Tiện lợi:** Tận dụng thời gian rảnh ngắn.
2. **Không áp lực:** Không có bài kiểm tra, chỉ có trò chuyện.
3. **Tính thực tế cao:** Giải quyết vấn đề "học mãi không dùng được".

---
*Tham khảo thêm:*

* [Strategic Analysis](strategic_analysis.md): Phân tích sâu về tâm lý và chiến lược.
* [Learning Methodology](learning_methodology.md): Chi tiết về phương pháp giáo dục.
* [Technical Strategy](technical_strategy.md): Kiến trúc hệ thống và công nghệ.
