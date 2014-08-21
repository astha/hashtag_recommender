rm -f results
touch results
for feature in presence tf tfidf
do
	for ranking_approach in {1..3}
	do
		for k in 5 10 15 20
		do
			python basic_recommenders.py $1 $feature $ranking_approach $k >> results
		done
	done
done