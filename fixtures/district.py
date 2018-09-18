districts = ['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island', 'New Jersey', 'Long Island', 'Westchester', 'Fairfield']

for ii in districts:
	City.objects.create(name=ii, state_id=3956, district_id=48019)
