const localStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {}, clear: () => {} };
global.localStorage = localStorage;
