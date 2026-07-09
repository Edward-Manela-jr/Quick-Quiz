-- Run this in the Supabase SQL editor.
-- Allows the same email to submit different quizzes, while blocking duplicate
-- attempts for the same quiz.

ALTER TABLE quiz_results2 DROP CONSTRAINT IF EXISTS quiz_results2_email_key;

ALTER TABLE quiz_results2
  ADD CONSTRAINT quiz_results2_email_quiz_id_key UNIQUE (email, quiz_id);
