INSERT INTO platform_llm (id, display_name, model_name, provider, is_active, created_at, updated_at)
VALUES
    (gen_random_uuid(), 'GPT-4o Mini (Free)', 'gpt-4o-mini', 'openai', true, NOW(), NOW()),
    (gen_random_uuid(), 'Gemini 2.0 Flash (Free)', 'gemini-2.0-flash', 'google', true, NOW(), NOW())
ON CONFLICT DO NOTHING;