int age = 20;
int total = 0;
int i = 0;

if (age >= 18 && age < 60) {
    total = age + 5;
} else {
    total = 0;
}

while (i < 3) {
    total += i;
    i++;
}

for (int j = 0; j < 5; j++) {
    total += j;
}

do {
    i--;
} while (i > 0);
