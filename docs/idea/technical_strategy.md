# NudgeEn: Chiến lược Kỹ thuật (Technical Strategy)

## 1. Kiến trúc Dual-Agent (Bộ não kép)

Hệ thống được chia thành hai thực thể độc lập để tối ưu hóa trải nghiệm "Shadow Learning" và chi phí vận hành.

### 1.1. Buddy Agent (Interaction)

* **Mục tiêu:** Tốc độ phản hồi cực nhanh (< 2s), duy trì "Vibe", gắn kết cảm xúc.
* **Model gợi ý:** SLM (Small Language Model) như **Qwen-7B**, **Llama-3-8B** hoặc **Mistral-7B**.
* **Host:** Tự host (Ollama/vLLM) hoặc dùng model cực rẻ (Gemini Flash) để đảm bảo độ trễ thấp.
* **Nhiệm vụ:** Greeting, small talk, phản hồi cảm xúc, duy trì mạch hội thoại.

### 1.2. Analyst Agent (Shadow)

* **Mục tiêu:** Độ chính xác học thuật cao, phân tích lỗi sâu.
* **Model gợi ý:** LLM mạnh như **Gemini 1.5 Pro** hoặc **GPT-4o**.
* **Nhiệm vụ:**
  * Soi lỗi ngữ pháp/từ vựng (ngầm).
  * Phân loại kiến thức (Knowledge Points).
  * Tổng hợp Dashboard tiến độ và Evidence Archive.
  * Chuẩn bị context cho "Implicit Feedback" gửi cho Buddy Agent.

## 2. Chiến lược Hybrid Model & Tối ưu Chi phí

* **Tầng 1 (Interaction Layer):** 90% traffic do Buddy Agent xử lý.
* **Tầng 2 (Analysis Layer):** Analyst Agent chỉ can thiệp định kỳ hoặc theo sự kiện (Event-driven):
  * Phân tích và tổng hợp Recap (ví dụ: cuối ngày/tuần).
  * Cần phân tích sâu hoặc chuẩn bị "Implicit Feedback" cho các chu kỳ tiếp theo.
  * Người dùng yêu cầu giải thích cụ thể (Deep Talk).

## 3. Hệ thống Trí nhớ & Quản lý Hội thoại (Memory & Context)

NudgeEn sử dụng mô hình **Single Story Chat** (một luồng hội thoại duy nhất và liên tục, giống như nhắn tin với người thật).

* **Single Story Chat:** Không chia session, không bắt đầu lại từ đầu. Lịch sử chat được lưu trữ như một dòng thời gian duy nhất.
* **Long-term Memory:** Sử dụng **PostgreSQL (JSONB)** kết hợp với **PGVector**.
* **UserGraph (Entity Extraction):** Analyst Agent trích xuất các thông tin quan trọng (sở thích, sự kiện, nỗi sợ) định kỳ để cập nhật hồ sơ người dùng.
* **Context Window Management:** Hệ thống sẽ tự động tối ưu hóa Context Window (sử dụng kỹ thuật Summary Buffering, Sliding Window hoặc RAG) để đảm bảo Buddy Agent luôn nắm bắt được các tình tiết quan trọng mà không làm "ngợp" model.

## 4. Kiểm thử & Độ tin cậy (Testability)

* **Dialogue Integration:** Chạy các kịch bản mẫu để kiểm tra tính nhất quán của Vibe và khả năng gợi nhớ thông tin cũ.
* **Shadow Accuracy:** Kiểm tra độ chính xác của Analyst Agent trong việc phát hiện lỗi.
* **Latency Benchmarks:** Đảm bảo thời gian phản hồi của Buddy Agent luôn < 2s.

---
*Tham khảo thêm:*

* [Product Vision](product_vision.md): Tổng quan ý tưởng.
* [Learning Methodology](learning_methodology.md): Phương pháp giáo dục.
* [Strategic Analysis](strategic_analysis.md): Phân tích chiến lược.
