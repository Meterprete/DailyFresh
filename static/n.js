var arr = [
    {"name": "张三", "id": 1, age: 18},
    {"name": "李四", "id": 2, age: 19},
    {"name": "张三", "id": 3, age: 18},
    {"name": "张三", "id": 4, age: 20},
    {"name": "小明", "id": 5, age: 17},
    {"name": "小白", "id": 6, age: 18}
];
let tempArr = [];
let newarr = [];
for (let i = 0; i < arr.length; i++) {
    if (tempArr.indexOf(arr[i].name) === -1) {
        newarr.push({
            name: arr[i].name,
            origin: [arr[i]]
        });
        tempArr.push(arr[i].name);
    } else {
        for (let j = 0; j < newarr.length; j++) {
            if (newarr[j].name === arr[i].name) {
                newarr[j].origin.push(arr[i]);
                break;
            }
        }
    }
}
console.log(newarr);
