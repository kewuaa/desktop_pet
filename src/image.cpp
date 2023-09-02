#include <iostream>
#include <vector>
#include <random>
#include <filesystem>
#include <fstream>
#include <time.h>

#include "QtWidgets/QLabel"
#include "QtGui/QPixmap"
#include "QtGui/QImage"
#include "QtGui/QIcon"
#include "cJSON.h"

namespace PetImage {

static std::vector<std::vector<QImage> > actions;

void load() {
    char path[1024];
    int len = std::sprintf(path, "%s/../desktop_pet/image", __FILE__);
    path[len] = 0;
    if (!std::filesystem::exists(path)) {
        throw std::runtime_error("path not exists");
    }
    std::filesystem::directory_entry dir(path);
    if (dir.status().type() != std::filesystem::file_type::directory) {
        throw std::runtime_error("not a directory");
    }
    int count = 0;
    std::vector<std::string> pets;
    pets.reserve(4);
    for (auto& it: std::filesystem::directory_iterator(path)) {
        if (it.status().type() == std::filesystem::file_type::directory) {
            if (std::filesystem::exists(it.path().string() + "/pet.json")) {
                count += 1;
                pets.push_back(it.path().filename().string());
            }
        }
    }

    srand(time(NULL));
    const char* pet = pets[rand() % count].data();
    len = std::sprintf(path, "%s/../desktop_pet/image/%s/pet.json", __FILE__, pet);
    path[len] = 0;
    std::ifstream f;
    f.open(path, std::ios::in);
    f.seekg(0, f.end);
    const int file_size = f.tellg();
    f.seekg(0, f.beg);
    char* buffer = new char[file_size + 1];
    buffer[file_size] = 0;
    f.read(buffer, file_size);
    cJSON* root = cJSON_Parse(buffer);
    cJSON* item;

    item = cJSON_GetObjectItem(root, "img_format");
    const char* format = item ? item->valuestring : "jpg";

    item = cJSON_GetObjectItem(root, "actions");
    if (item) {
        const int action_num = cJSON_GetArraySize(item);
        actions.reserve(action_num);
        cJSON* array_item;
        int action_size;
        for (unsigned int i = 0; i < action_num; i++) {
            array_item = cJSON_GetArrayItem(item, i);
            if (!array_item) {
                throw std::runtime_error("parse json error");
            }
            actions.emplace_back();
            action_size = cJSON_GetArraySize(array_item);
            actions[i].reserve(action_size);
            cJSON* inner_array_item;
            for (unsigned int j = 0; j < action_size; j++) {
                inner_array_item = cJSON_GetArrayItem(array_item, j);
                if (!inner_array_item) {
                    throw std::runtime_error("parse json error");
                }
                len = std::sprintf(path, "%s/../desktop_pet/image/%s/%s.%s", __FILE__, pet, inner_array_item->valuestring, format);
                path[len] = 0;
                actions[i].emplace_back(path);
            }
        }
    } else throw std::runtime_error("could not get \"actions\" key");
    delete[] buffer;
    cJSON_Delete(root);
}

static
std::vector<QImage>& random_action() {
    return actions[rand() % actions.capacity()];
}

void set(QLabel& label) {
    static std::vector<QImage>& action = random_action();
    static std::vector<QImage>::iterator p = action.begin();
    label.setPixmap(QPixmap::fromImage(*p));
    p += 1;
    if (p == action.end()) {
        action = random_action();
        p = action.begin();
    }
}

QIcon get_icon() {
    return {QPixmap::fromImage(actions[0][0])};
}
}
