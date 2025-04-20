import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

# 크롤링할 위키피디아 URL
url = 'https://en.wikipedia.org/wiki/Java_(programming_language)'

# 웹 페이지 요청 및 파싱
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# 모든 문단을 하나의 문자열로 결합
all_text = ' '.join(p.get_text().strip() for p in soup.find_all('p') if p.get_text().strip())

# 단어 빈도 계산
word_counts = Counter(all_text.split())

# 단어 빈도 시각화 (상위 10개 단어)
most_common_words = word_counts.most_common(10)
words, counts = zip(*most_common_words)

plt.figure(figsize=(10, 6))
plt.bar(words, counts)
plt.title('Top 10 Words in Wikipedia Article')
plt.xlabel('Words')
plt.ylabel('Frequency')
plt.xticks(rotation=45)
plt.grid(axis='y')
plt.tight_layout()
plt.savefig('top_words_plot.png')

# 전체 단어 빈도를 DataFrame으로 변환하고 정렬
df = pd.DataFrame(word_counts.items(), columns=['Word', 'Frequency']).sort_values(by='Frequency', ascending=False)


# CSV 파일로 저장
df.to_csv('word_frequency.csv', index=False)  # 인덱스를 저장하지 않음