import enum


class OrderTypeEnum(enum.Enum):
	oldest = 'oldest'
	latest = 'latest'
	random = 'random'


class StudyTypeEnum(enum.Enum):
	one_off = 'one_off'
	recurrent = 'recurrent'
