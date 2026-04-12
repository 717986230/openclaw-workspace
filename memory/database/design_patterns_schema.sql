-- 前端设计模式数据库结构
-- 用于存储和匹配相似风格的设计系统

-- 1. 设计系统表
CREATE TABLE IF NOT EXISTS design_systems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,           -- 网站名称 (如: claude, vercel, linear)
    category TEXT NOT NULL,               -- 分类 (ai, devtools, fintech, etc.)
    url TEXT,                            -- 原始网站 URL
    description TEXT,                    -- 描述
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 色彩系统表
CREATE TABLE IF NOT EXISTS color_palettes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    design_system_id INTEGER NOT NULL,
    role TEXT NOT NULL,                  -- primary, secondary, neutral, semantic
    name TEXT NOT NULL,                  -- 颜色名称
    hex TEXT NOT NULL,                   -- 十六进制值
    usage TEXT,                          -- 使用说明
    FOREIGN KEY (design_system_id) REFERENCES design_systems(id) ON DELETE CASCADE
);

-- 3. 排版系统表
CREATE TABLE IF NOT EXISTS typography_systems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    design_system_id INTEGER NOT NULL,
    font_family TEXT NOT NULL,           -- 字体家族
    font_type TEXT NOT NULL,             -- sans-serif, serif, monospace
    font_size TEXT,                      -- 字体大小
    font_weight TEXT,                    -- 字重
    line_height TEXT,                    -- 行高
    letter_spacing TEXT,                 -- 字间距
    usage TEXT,                          -- 使用场景
    FOREIGN KEY (design_system_id) REFERENCES design_systems(id) ON DELETE CASCADE
);

-- 4. 组件样式表
CREATE TABLE IF NOT EXISTS component_styles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    design_system_id INTEGER NOT NULL,
    component_type TEXT NOT NULL,        -- button, card, input, nav, etc.
    variant TEXT,                        -- primary, secondary, ghost, etc.
    css_properties TEXT,                 -- JSON 格式的 CSS 属性
    html_example TEXT,                   -- HTML 示例
    FOREIGN KEY (design_system_id) REFERENCES design_systems(id) ON DELETE CASCADE
);

-- 5. 布局系统表
CREATE TABLE IF NOT EXISTS layout_systems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    design_system_id INTEGER NOT NULL,
    spacing_scale TEXT,                  -- JSON 格式的间距系统
    container_width TEXT,               -- 容器宽度
    grid_system TEXT,                    -- JSON 格式的网格系统
    breakpoints TEXT,                   -- JSON 格式的断点
    FOREIGN KEY (design_system_id) REFERENCES design_systems(id) ON DELETE CASCADE
);

-- 6. 设计风格标签表
CREATE TABLE IF NOT EXISTS design_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    design_system_id INTEGER NOT NULL,
    tag TEXT NOT NULL,                   -- dark, minimal, colorful, etc.
    FOREIGN KEY (design_system_id) REFERENCES design_systems(id) ON DELETE CASCADE
);

-- 7. 设计相似度表
CREATE TABLE IF NOT EXISTS design_similarities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    design_system_1_id INTEGER NOT NULL,
    design_system_2_id INTEGER NOT NULL,
    similarity_score REAL NOT NULL,      -- 0-1 相似度分数
    similarity_reason TEXT,              -- 相似原因
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (design_system_1_id) REFERENCES design_systems(id) ON DELETE CASCADE,
    FOREIGN KEY (design_system_2_id) REFERENCES design_systems(id) ON DELETE CASCADE,
    UNIQUE(design_system_1_id, design_system_2_id)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_design_systems_category ON design_systems(category);
CREATE INDEX IF NOT EXISTS idx_color_palettes_design_system ON color_palettes(design_system_id);
CREATE INDEX IF NOT EXISTS idx_typography_design_system ON typography_systems(design_system_id);
CREATE INDEX IF NOT EXISTS idx_component_design_system ON component_styles(design_system_id);
CREATE INDEX IF NOT EXISTS idx_layout_design_system ON layout_systems(design_system_id);
CREATE INDEX IF NOT EXISTS idx_tags_design_system ON design_tags(design_system_id);
CREATE INDEX IF NOT EXISTS idx_similarities_score ON design_similarities(similarity_score);
