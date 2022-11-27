function combinations() {
	return [...arguments].reduce((total, value) => value===0 ? total : total * value)
}

console.log(combinations(2,4,5,6));