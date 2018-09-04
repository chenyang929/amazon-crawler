import re

u = 'https://www.amazon.co.uk/product-reviews/B0719585LS/?pageNumber=1&pageSize=50&filterByStar=three_star'

print(re.sub(r'pageNumber=(\d)', 'pageNumber=2', u))
u1 = 'https://www.amazon.com/product-reviews/B0719585LS/?&pageNumber=1&pageSize=50'
