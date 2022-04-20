### def \_\_init__(self, index: SearchIndex, stop_words: iter, range_algorithm: callable = None)
Принимает объект класса SearchIndex, переменную со стоп словами и опционально 
функцию ранжирования и инициализирует объект класса SearchQueryGenerator. 
Если функция ранжирования не задана, то использует стандартную.