import _ from 'lodash';

class ValueFilter {
  constructor(value) {
    this.value = value;
  }

  static isFiltered() {
    return true;
  }
}

class ValueFilterNot extends ValueFilter {
  constructor(filter) {
    super('');
    this.filter = filter;
  }

  isFiltered(orginal) {
    return !this.filter.isFiltered(orginal);
  }
}
/* class ValueFilterAnd extends ValueFilter {
  constructor(filter1, filter2) {
    super('');
    this.filter1 = filter1;
    this.filter2 = filter2;
  }

  isFiltered(orginal) {
    return this.filter1.isFiltered(orginal) && this.filter2.isFiltered(orginal);
  }
} */
/* class ValueFilterOr extends ValueFilter {
  constructor(filter1, filter2) {
    super('');
    this.filter1 = filter1;
    this.filter2 = filter2;
  }

  isFiltered(orginal) {
    return this.filter1.isFiltered(orginal) || this.filter2.isFiltered(orginal);
  }
} */

class ValueFilterEqual extends ValueFilter {
  /* constructor(value) {
    super(value);
  }
 */
  isFiltered(orginal) {
    return _.eq(this.value, orginal) || this.value === orginal;
  }
}

class ValueFilterGt extends ValueFilter {
  /* constructor(value) {
    super(value);
  } */

  isFiltered(orginal) {
    return _.gt(this.value, orginal);
  }
}
class ValueFilterGte extends ValueFilter {
  /* constructor(value) {
    super(value);
  } */

  isFiltered(orginal) {
    return _.gte(this.value, orginal);
  }
}
class ValueFilterLt extends ValueFilter {
  /* constructor(value) {
    super(value);
  } */

  isFiltered(orginal) {
    return _.lt(this.value, orginal);
  }
}
class ValueFilterLte extends ValueFilter {
  /* constructor(value) {
    super(value);
  } */

  isFiltered(orginal) {
    return _.lte(this.value, orginal);
  }
}
class ValueFilterBetween extends ValueFilter {
  constructor(value1, value2) {
    super(value1);
    this.value2 = value2;
  }

  isFiltered(orginal) {
    return _.inRange(orginal, this.value, this.valu2);
  }
}

class ValueFilterEndsWith extends ValueFilter {
  /* constructor(value) {
    super(value);
  } */

  isFiltered(orginal) {
    return _.endsWith(this.value, orginal);
  }
}
class ValueFilterStartsWith extends ValueFilter {
  /* constructor(value) {
    super(value);
  } */

  isFiltered(orginal) {
    return _.startsWith(this.value, orginal);
  }
}
class ValueFilterContains extends ValueFilter {
  /* constructor(value) {
    super(value);
  } */

  isFiltered(orginal) {
    return _.includes(orginal, this.value);
  }
}

const ValueFilterMap = {
  '=': value => new ValueFilterEqual(value),
  '!=': value => new ValueFilterNot(new ValueFilterEqual(value)),
  startwith: value => new ValueFilterStartsWith(value),
  '!startwith': value => new ValueFilterNot(new ValueFilterStartsWith(value)),
  endwith: value => new ValueFilterEndsWith(value),
  '!endwith': value => new ValueFilterNot(new ValueFilterEndsWith(value)),
  contains: value => new ValueFilterContains(value),
  '!contains': value => new ValueFilterNot(new ValueFilterContains(value)),
  '<': value => new ValueFilterLt(value),
  '=<': value => new ValueFilterLte(value),
  '=>': value => new ValueFilterGte(value),
  '>': value => new ValueFilterGt(value),
  between: (value1, value2) => new ValueFilterBetween(value1, value2),
  '!between': (value1, value2) => new ValueFilterNot(new ValueFilterBetween(value1, value2)),
};

export default ValueFilterMap;
