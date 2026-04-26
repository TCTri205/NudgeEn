# NudgeEn: Phương pháp Luận Học tập (Learning Methodology)

## 1. Triết lý "Shadow Learning" (Học trong bóng tối)

Thay vì buộc người dùng phải "đi học", NudgeEn đưa việc học vào "bóng tối" của một cuộc hội thoại giải trí.

### A. Immersion Flow vs. Shadow Flow

* **Immersion Flow:** Người dùng chat với **Buddy Agent** (Persona). Mục tiêu duy nhất là sự kết nối cảm xúc và sự liền mạch. AI không bao giờ ngắt lời để sửa lỗi trực tiếp.
* **Shadow Flow:** **Analyst Agent** âm thầm quan sát, bóc tách cấu trúc câu, phát hiện lỗi sai và lưu vào database để phục vụ Recap và Implicit Feedback.

## 2. Các Kỹ thuật Giáo dục Đặc biệt

### 2.1. Implicit Feedback (Phản hồi ngầm)

Đây là kỹ thuật dạy học tinh tế nhất. Khi người dùng dùng sai một cấu trúc hoặc từ vựng, AI sẽ không chỉ trích. Thay vào đó, trong câu trả lời tiếp theo, AI sẽ chủ động sử dụng lại chính ý tưởng đó nhưng với **cấu trúc đúng**.

* *Ví dụ:*
  * User: "I go to movie yesterday."
  * **Buddy Agent:** "Oh, that's cool! I **went to the movies** a few weeks ago too. What film did you see?"

### 2.2. Adaptive Re-entry (Tái hòa nhập thích ứng)

Giải quyết "áp lực tội lỗi" khi bỏ học. AI sẽ nhắn tin dựa trên nội dung cũ để mở lại hội thoại một cách tự nhiên nhất.

* *Nguyên tắc:* Không bao giờ dùng câu: "Đã lâu bạn không học". Thay bằng: "Này, hôm trước bạn bảo chuẩn bị đi du lịch, chuyến đi thế nào rồi?"

### 2.3. Scaffolding (Giàn giáo kiến thức)

AI điều chỉnh độ phức tạp của câu trả lời dựa trên nỗ lực của người dùng (Average Word Count - AWC). Nếu người dùng viết câu ngắn, AI sẽ phản hồi tương ứng nhưng thỉnh thoảng "cài cắm" thêm 1-2 từ vựng cấp độ cao hơn (C1/C2) để kích thích sự tò mò.

## 3. Cụ thể hóa Kết quả (Tangible Results)

Hệ thống biến sự tiến bộ "vô hình" thành dữ liệu có thể nhìn thấy:

* **Fluency Score:** Đo lường qua 3 chỉ số:
  * **Vocabulary Breadth:** Số lượng từ vựng độc nhất đã sử dụng.
  * **Syntactic Complexity:** Độ phức tạp của cấu trúc câu.
  * **Response Momentum:** Tốc độ và tần suất phản hồi.
* **The Evidence Archive (Kho lưu trữ bằng chứng):**
  * Recap hàng tuần không chỉ liệt kê lỗi. Nó là một cuốn "nhật ký tiến bộ".
  * "Tuần này bạn đã sử dụng thành công 15 cấu trúc câu phức và thuyết phục được Buddy Agent trong tình huống đàm phán giả lập."

## 4. Cân bằng "Vibe" và "Kết quả"

* **Vibe (Entertainment):** Là "mồi nhử" (Hook) để người dùng quay lại mỗi ngày.
* **Results (Learning):** Là "phần thưởng" (Reward) để người dùng cảm thấy thời gian bỏ ra là xứng đáng.

NudgeEn thành công khi người dùng coi việc chat với AI là một nhu cầu giải trí, nhưng cuối mỗi tuần họ lại ngạc nhiên vì khả năng tiếng Anh của mình đã tăng lên đáng kể.

---
*Tham khảo thêm:*

* [Product Vision](product_vision.md): Tổng quan ý tưởng.
* [Strategic Analysis](strategic_analysis.md): Phân tích chiến lược.
* [Technical Strategy](technical_strategy.md): Kiến trúc hệ thống và công nghệ.
