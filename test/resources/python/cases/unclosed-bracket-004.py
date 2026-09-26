print(doc('design'))
print(grep({'query':['output_reasoning_tokens','llm_reasoning_tokens','reasoning'], 'paths':[project_root_path / 'apps/vis-companion/src/components'], 'context':1})[:6500]
print(grep({'query':['output_reasoning_tokens','llm_reasoning_tokens','reasoning-tokens'], 'paths':[project_root_path / 'src/com/blockether/vis/internal/gateway'], 'context':2})[:8000])