#include <iostream>
#include <variant>
#include <vector>
#include <unordered_map>
#include <functional>
#include <sstream>
#include <fstream>

using StackValue = std::variant<int, std::string>;

std::vector<StackValue> stack;
std::vector<StackValue> ret_stack;

// Not gonna lie, I will do something to this thing...
StackValue memory[1000];

std::unordered_map<std::string, std::function<void()>> builtins;
std::unordered_map<std::string, std::pair<int, std::function<void()>>> compile_words;

std::unordered_map<std::string, std::string> functions;
std::string body;

int r = 1;
int compiling = 0;

#define to_int(obj) std::get<int>(obj)
#define to_str(obj) std::get<std::string>(obj).c_str()

inline void push(StackValue val) {
    stack.push_back(val);
}

inline StackValue pop() {
    StackValue obj = stack.back(); 
    stack.pop_back();
    return obj;
}

// Prototypes???
void run(std::string);
void run_file(std::string);

// Inlined, because we use this only once
inline void InitBuiltins() {
    builtins["+"] = []() {int b = to_int(pop()); int a = to_int(pop()); push(a + b);};
    builtins["-"] = []() {int b = to_int(pop()); int a = to_int(pop()); push(a - b);};
    builtins["*"] = []() {int b = to_int(pop()); int a = to_int(pop()); push(a * b);};
    builtins["/"] = []() {int b = to_int(pop()); int a = to_int(pop()); push(a / b);};
    builtins["%"] = []() {int b = to_int(pop()); int a = to_int(pop()); push(a % b);};

    builtins["<"] = []() {int b = to_int(pop()); int a = to_int(pop()); push(a < b);};
    builtins[">"] = []() {int b = to_int(pop()); int a = to_int(pop()); push(a > b);};
    builtins["=="] = []() {StackValue b = pop(); StackValue a = pop(); push(a == b);};
    builtins["!="] = []() {int b = to_int(pop()); int a = to_int(pop()); push(a != b);};
    builtins[">="] = []() {int b = to_int(pop()); int a = to_int(pop()); push(a >= b);};
    builtins["<="] = []() {int b = to_int(pop()); int a = to_int(pop()); push(a <= b);};

    builtins["and"] = []() {int b = to_int(pop()); int a = to_int(pop()); push(a & b);};
    builtins["or"] = []() {int b = to_int(pop()); int a = to_int(pop()); push(a | b);};
    builtins["xor"] = []() {int b = to_int(pop()); int a = to_int(pop()); push(a ^ b);};
    builtins["not"] = []() {int a = to_int(pop()); push(~a);};

    builtins["import"] = []() {run_file(to_str(pop()));};

    builtins["!"] = []() {int addr = to_int(pop()); StackValue value = pop(); memory[addr] = value;};
    builtins["@"] = []() {push(memory[to_int(pop())]);};

    builtins["."] = []() {
        StackValue value = pop();
        if (std::holds_alternative<int>(value)) {
            std::cout << std::get<int>(value) << " ";
        } else {
            std::cout << std::get<std::string>(value) << " ";
        }
    };
    builtins["emit"] = []() {printf("%c", to_int(pop()));};
    builtins[","] = []() {push(getchar_unlocked());};

    builtins["nl"] = []() {std::cout << std::endl;};

    builtins["print"] = []() {builtins["."](); builtins["nl"]();};
    builtins["input"] = []() {std::string line; std::getline(std::cin, line); push(line);};

    builtins["dup"] = []() {push(stack.back());};
    builtins["swap"] = []() {StackValue a = pop(); StackValue b = pop(); push(a); push(b);};
    builtins["over"] = []() {push(stack[stack.size() - 2]);};
    builtins["drop"] = []() {pop();};
    builtins["depth"] = []() {push(static_cast<int>(stack.size()));};
    builtins["clear"] = []() {stack.clear();};

    builtins["stoi"] = []() {push(std::stoi(std::get<std::string>(pop())));};
    // builtins["type"] = []() {push(typeid(pop()).name());};

    builtins[">r"] = []() {ret_stack.push_back(pop());};
    builtins["r>"] = []() {StackValue obj = ret_stack.back(); ret_stack.pop_back(); push(obj);};
    builtins["r@"] = []() {push(ret_stack.back());};

    builtins["{"] = []() {compiling += 1;};
    builtins["if"] = []() {compiling += 2;};
    builtins["\""] = []() {compiling += 3;};

    builtins["bye"] = []() {r = 0;};

    compile_words["}"] = {1, 
        []() {
            std::string name = to_str(pop());
            functions[name] = body;
        }
    };
    compile_words["then"] = {2,
        []() {
            int cond = to_int(pop());

            std::string local_body = body;
            body.clear();

            if (cond) {
                run(local_body);
            }
        }
    };
    compile_words["\""] = {3,
        []() {
            body.erase(0, 1);
            push(body);
        }
    };
}

void run(std::string line) {
    std::stringstream ss(line);
    std::string token;

    while (ss >> token) {
        if (compiling) {
            if (compile_words.count(token)) {
                if ((compiling - compile_words[token].first) >= 0)
                    compiling -= compile_words[token].first;
                    if (compiling == 0) {
                        compile_words[token].second();
                        body.clear();
                    }
                    else {
                        body += ' ';
                        body += token;
                    }
            } else {
                if (token == "if" || token == "{" || token == "\"") {
                    builtins[token]();
                }
                body += ' ';
                body += token;
            }
        } else {
            if (functions.count(token)) {
                run(functions[token]);
            } else if (builtins.count(token)) {
                builtins[token]();
            } else {
                try {
                    size_t p;
                    int val = std::stoi(token, &p);
                    if (p == token.length()) {
                        push(std::stoi(token)); 
                    }
                    else {
                        push(token); 
                    }
                } catch (...) {
                    push(token);
                }
            }
        }
    }
}

void run_file(std::string _file) {
    std::ifstream file(_file);

    if (file.is_open()) {
        std::ostringstream ss;
        ss << file.rdbuf();
        run(ss.str());
    }
}

int main(int argc, char** argv) {    
    InitBuiltins();
    if (argc >= 2) {
        for (int i = 1; i < argc; i++) {
            run_file(argv[i]);
        }
    } else {
        std::cout << "Usage: <compiler binary> [files]" << std::endl;
        r = 0;
    }

    std::string line;
    while (r && std::getline(std::cin, line)) {
        run(line);
    }
    return 0;
}
