from math import *
AU = 1.5e8
mins = 60
hours = 60*mins
days = 24*hours
yr = 365.25*days

T = 1*yr

E = radians(23.44)
omega = 2*pi/(23.9345*hours)
t_eq = 31*days + 29*days + 19*days + 4.5*hours
lng0 = radians(-154.74)

months = [
	(31, "Jan"),
	(60, "Feb"),
	(91, "Mar"),
	(121, "Apr"),
	(152, "May"),
	(182, "Jun"),
	(213, "Jul"),
	(244, "Aug"),
	(274, "Sep"),
	(305, "Oct"),
	(335, "Nov"),
	(366, "Dec")
	]

def toSeconds(M,d,h,m):

	last_month = 0
	for i,j in months:
		if j == M:
			return last_month*days + (d-1)*days + (h+5)*hours + m*mins
		last_month = i
	return "Invalid"

def toDateTime(t):
	values = []
	d = trunc(t/days)
	rem = (t/days - d)
	h = trunc(rem*24)
	rem = rem*24 - h
	m = trunc(rem*60)

	last_month = 0
	for i,j in months:
		if d+1 <= i:
			values.append(j)
			values.append(str(d+1-last_month))
			values.append("2016 @ {0}:{1} UTC {2}:{1} EST".format(h, m, h-5 if h-5>0 else h+19))
			return " ".join(values)
		last_month = i
	return "Invalid"

class Matrix: 
	cols = 0
	rows = 0
	values = []

	def __init__(self, m, n, v):
		assert m == len(v)
		for row in v:
			assert n == len(row) 
		self.rows = m
		self.cols = n
		self.values = v

	def __getitem__(self, tup):
		i, j = tup
		return self.values[i][j]

	def __setitem__(self, tup, val):
		i, j = tup
		self.values[i][j] = val

	def __mul__(A, B):
		assert(A.cols == B.rows)
		n = A.rows
		m = A.cols
		p = B.cols
		
		values = []
		
		for i in range(0, n):
			row = []
			for j in range(0, p):
				s = 0
				for k in range(0, m):
					s += A[i,k] * B[k,j]
				row.append(s)
			values.append(row)

		return Matrix(n, p, values)

def Vector(x, y, z):
	return Matrix(3,1, [[x], [y], [z]])

def Rx(t):
	cos_t = cos(t)
	sin_t = sin(t)
	return Matrix(3,3, [
		[1, 0    ,  0],
		[0, cos_t, -sin_t],
		[0, sin_t,  cos_t] ])

def Ry(t):
	cos_t = cos(t)
	sin_t = sin(t)
	return Matrix(3,3, [
		[ cos_t, 0, -sin_t],
		[ 0    , 1, 0    ],
		[sin_t,  0, cos_t] ])

def Rz(t):
	cos_t = cos(t)
	sin_t = sin(t)
	return Matrix(3,3, [
		[ cos_t, sin_t, 0],
		[-sin_t, cos_t, 0],
		[ 0,     0,     1] ])

def theta_approx(t):
	return 2*pi*(t-t_eq)/T

def theta_exact(t):
	M_ = M(t)
	e_ = 0.0167
	return M_ + 2*e_*sin(M_) + (5/4)*(e_**2)*sin(2*M_)

def M(t):
	tau = 2*days+23*hours
	return 2*pi*(t-tau-t_eq)/T

def Calculate_Sun_position(t, L, lng):
	t0 = t_eq - (lng - lng0)/omega
	p = theta_exact(t)
	r = Vector(cos(p), sin(p), 0)
	return Rx(pi/2-L)*Rz(omega*(t-t0))*Rx(E)*r

def Altitude(R_sun):
	z = R_sun[2,0]
	return degrees(asin(z))

def Azimuth(R_sun):
	x = R_sun[0,0]
	y = R_sun[1,0]
	return 270 - degrees(atan(y/x))

def Output_Human_Readable(R_sun, t):
	altitude = Altitude(R_sun)
	azimuth = Azimuth(R_sun)
	degrees_relative_to_West = abs(azimuth-270)
	n_or_s = "North" if azimuth-270 > 0 else "South"

	time_in_days = str((t)/days)
	date = toDateTime(t)

	return "Time: {0} days \n \
	{1}\n \
	Altitude: {2} degrees\n \
	Azimuth: {3} degrees\n \
	{4} degrees {5} of due West\n\
	-------------------------------------\n".format(time_in_days, date, altitude, azimuth, degrees_relative_to_West, n_or_s)

def Output_CSV(obs_data, filename):
	data_string = ""
	for row in obs_data:
		data_string += ",".join(row) + "\n"

	f = open(filename, 'w')
	f.write(data_string)
	f.close()

def main():
	L =  radians(33.775072)
	lng = radians(-84.397262)

	observations = [
		["Aug", 28, 18, 48, -6],
		["Sep",  5, 18, 40, -0.8],
		["Sep", 14, 18, 30, 3.2],
		["Sep", 28, 18, 14, 4],
		["Oct", 11, 17, 48, 10],
		["Oct", 18, 17, 45, 15.2],
		["Oct", 28, 17, 30, 18.4],
		["Nov", 13, 17, 13, 28.8]
	]

	NOAA = [
		["Aug", 28, 18, 48, -9],
		["Sep",  5, 18, 40, -5.9],
		["Sep", 14, 18, 30, 2],
		["Sep", 28, 18, 14, 4],
		["Oct", 11, 17, 48, 11.3],
		["Oct", 18, 17, 45, 13.5],
		["Oct", 28, 17, 30, 18.3],
		["Nov", 13, 17, 13, 24.7]
	]

	times = []
	for obs in observations:
		times.append(toSeconds(obs[0], obs[1], obs[2], obs[3]))

	obs_data = [
		["","13-Nov-16","28-Oct-16","18-Oct-16","11-Oct-16","28-Sep-16","14-Sep-16","5-Sep-16,""28-Aug-16"],
		["NOAA", str(NOAA[7][4]), str(NOAA[6][4]), str(NOAA[5][4]), str(NOAA[4][4]), str(NOAA[3][4]), str(NOAA[2][4]),str(NOAA[1][4]), str(NOAA[0][4])],
		["observed", str(observations[7][4]), str(observations[6][4]), str(observations[5][4]), str(observations[4][4]), str(observations[3][4]), str(observations[2][4]),str(observations[1][4]), str(observations[0][4])],
		["predicted"]
	]
	times.reverse()
	for time in times:
		R_sun = Calculate_Sun_position(time, L, lng)
		print(Output_Human_Readable(R_sun, time))
		obs_data[3].append(str(-(Azimuth(R_sun)-270)))

	Output_CSV(obs_data, "observations.csv")

	analemma_data = [
		["Analemma over Atlanta GA 2016", "Altitude", "Azimuth"]
	]

	t = 17*hours
	while(t/days < 366):
		R_sun = Calculate_Sun_position(t, L, lng)
		print(Output_Human_Readable(R_sun, t))

		analemma_data.append([toDateTime(t), str(Altitude(R_sun)), str(Azimuth(R_sun))])
		t+= 7*days

	Output_CSV(analemma_data, "analemma.csv")



if __name__ == '__main__':
	main()