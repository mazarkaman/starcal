#!/usr/bin/env python3
import math

from typing import Tuple, List, Optional, Generator

from scal3.cal_types import calTypes, to_jd, GREGORIAN
from scal3.time_utils import getEpochFromJd


def getMonthLen(year: int, month: int, calType: int) -> int:
	module, ok = calTypes[calType]
	if not ok:
		raise RuntimeError("cal type %r not found" % calType)
	return module.getMonthLen(year, month)


def monthPlus(y: int, m: int, p: int) -> Tuple[int, int]:
	y, m = divmod(y * 12 + m - 1 + p, 12)
	return y, m + 1


def dateEncode(date: Tuple[int, int, int]) -> str:
	return "%.4d/%.2d/%.2d" % tuple(date)


def dateEncodeDash(date: Tuple[int, int, int]) -> str:
	return "%.4d-%.2d-%.2d" % tuple(date)


def checkDate(date: Tuple[int, int, int]) -> None:
	if not 1 <= date[1] <= 12:
		raise ValueError("bad date %s (invalid month)" % date)
	if not 1 <= date[2] <= 31:
		raise ValueError("bad date %s (invalid day)" % date)


# FIXME: should return Tuple[int, int, int] ?
def dateDecode(st: str) -> List[int]:
	neg = False
	if st.startswith("-"):
		neg = True
		st = st[1:]
	if "-" in st:
		parts = st.split("-")
	elif "/" in st:
		parts = st.split("/")
	else:
		raise ValueError("bad date %s (invalid seperator)" % st)
	if len(parts) != 3:
		raise ValueError(
			"bad date %s (invalid numbers count %s)" % (st, len(parts))
		)
	try:
		date = [int(p) for p in parts]
	except ValueError:
		raise ValueError("bad date %s (omitting non-numeric)" % st)
	if neg:
		date[0] *= -1
	checkDate(date)
	return date


# FIXME: move to cal_types/
def validDate(calType: int, y: int, m: int, d: int) -> bool:
	if y < 0:
		return False
	if m < 1 or m > 12:
		return False
	if d > getMonthLen(y, m, calType):
		return False
	return True


def datesDiff(y1: int, m1: int, d1: int, y2: int, m2: int, d2: int) -> int:
	return to_jd(
		calType.primary,
		y2,
		m2,
		d2,
	) - to_jd(
		calType.primary,
		y1,
		m1,
		d1,
	)


def dayOfYear(y: int, m: int, d: int) -> int:
	return datesDiff(y, 1, 1, y, m, d) + 1


# FIXME: rename this function to weekDayByJd
# jwday: Calculate day of week from Julian day
# 0 = Sunday
# 1 = Monday
def jwday(jd: int) -> int:
	return (jd + 1) % 7


def getJdRangeForMonth(year: int, month: int, calType: int) -> Tuple[int, int]:
	day = getMonthLen(year, month, calType)
	return (
		to_jd(year, month, 1, calType),
		to_jd(year, month, day, calType) + 1,
	)


def getFloatYearFromJd(jd: int, calType: int) -> float:
	module, ok = calTypes[calType]
	if not ok:
		raise RuntimeError("cal type %r not found" % calType)
	year, month, day = module.jd_to(jd)
	yearStartJd = module.to_jd(year, 1, 1)
	nextYearStartJd = module.to_jd(year + 1, 1, 1)
	dayOfYear = jd - yearStartJd
	return year + float(dayOfYear) / (nextYearStartJd - yearStartJd)


def getJdFromFloatYear(fyear: float, calType: int) -> int:
	module, ok = calTypes[calType]
	if not ok:
		raise RuntimeError("cal type %r not found" % calType)
	year = int(math.floor(fyear))
	yearStartJd = module.to_jd(year, 1, 1)
	nextYearStartJd = module.to_jd(year + 1, 1, 1)
	dayOfYear = int((fyear - year) * (nextYearStartJd - yearStartJd))
	return yearStartJd + dayOfYear


def getEpochFromDate(y: int, m: int, d: int, calType: int) -> int:
	return getEpochFromJd(to_jd(
		y,
		m,
		d,
		calType,
	))


def ymdRange(
	date1: Tuple[int, int, int],
	date2: Tuple[int, int, int],
	calType: Optional[int] = None,
) -> Generator[Tuple[int, int, int], None, None]:
	y1, m1, d1 = date1
	y2, m2, d2 = date2
	if y1 == y2 and m1 == m2:
		for d in range(d1, d2):
			yield y1, m1, d
	if calType is None:
		calType = GREGORIAN
	module, ok = calTypes[calType]
	if not ok:
		raise RuntimeError("cal type %r not found" % calType)
	j1 = int(module.to_jd(y1, m1, d1))
	j2 = int(module.to_jd(y2, m2, d2))
	for j in range(j1, j2):
		yield module.jd_to(j)
