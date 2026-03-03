import pandas as pd
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from collections import Counter
import json

# 读取数据
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df

# 中文分词
def tokenize_chinese(text):
    words = jieba.cut(text)
    # 过滤停用词和短词
    stop_words = set(["的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这"])
    filtered_words = [word for word in words if word not in stop_words and len(word) > 1]
    return filtered_words

# 使用TF-IDF提取高频关键词
def extract_high_freq_words(texts, top_n=50):
    # 对文本进行分词
    tokenized_texts = [' '.join(tokenize_chinese(text)) for text in texts]
    
    # 使用TF-IDF进行向量化
    vectorizer = TfidfVectorizer(max_features=10000)
    X = vectorizer.fit_transform(tokenized_texts)
    
    # 提取关键词及其权重
    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = X.sum(axis=0).A1
    word_scores = [(feature_names[i], tfidf_scores[i]) for i in range(len(feature_names))]
    
    # 按权重排序并返回前N个
    word_scores.sort(key=lambda x: x[1], reverse=True)
    top_words = [word for word, score in word_scores[:top_n]]
    
    return top_words

# 使用LDA进行主题建模
def lda_topic_modeling(texts, n_topics=4, n_top_words=10):
    # 对文本进行分词
    tokenized_texts = [' '.join(tokenize_chinese(text)) for text in texts]
    
    # 使用CountVectorizer进行向量化
    vectorizer = CountVectorizer(max_features=10000)
    X = vectorizer.fit_transform(tokenized_texts)
    
    # 训练LDA模型
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42, n_jobs=-1)
    lda.fit(X)
    
    # 提取每个主题的关键词
    feature_names = vectorizer.get_feature_names_out()
    topics = {}
    
    for i, topic in enumerate(lda.components_):
        # 取每个主题的前N个关键词
        top_words_indices = topic.argsort()[-n_top_words:][::-1]
        top_words = [feature_names[idx] for idx in top_words_indices]
        topics[i] = top_words
    
    return topics

# 主函数
def main():
    # 读取数据
    input_file = "bilibili_endfield_comments_level6_stars1.csv"
    df = load_data(input_file)
    print(f"共读取 {len(df)} 条评论")
    
    # 提取评论内容
    texts = df['content'].tolist()
    
    # 使用TF-IDF提取高频关键词
    print("使用TF-IDF提取高频关键词...")
    high_freq_words = extract_high_freq_words(texts)
    print("\nTF-IDF高频关键词:")
    print(' '.join(high_freq_words))
    
    # 使用LDA进行主题建模
    print("\n使用LDA进行主题建模...")
    topics = lda_topic_modeling(texts)
    print("\nLDA主题建模结果:")
    for topic_id, topic_words in topics.items():
        print(f"主题 {topic_id}: {' '.join(topic_words)}")
    
    # 保存结果
    output_file = "tfidf_lda_analysis_result.json"
    result = {
        "high_freq_words": high_freq_words,
        "topics": topics
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n分析结果已保存到 {output_file}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()