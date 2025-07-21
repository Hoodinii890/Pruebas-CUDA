#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <random>

namespace py = pybind11;

int roll_card(py::object card_data) {
    if (!py::isinstance<py::list>(card_data)) {
        std::cout << "card_data no es una lista" << std::endl;
        return -1;
    }
    py::list cards = card_data.cast<py::list>();
    static std::random_device rd;
    static std::mt19937_64 gen(rd());

    while (true) {
        std::vector<int> candidates;
        for (size_t i = 0; i < len(cards); ++i) {
            if (!py::isinstance<py::dict>(cards[i])) {
                std::cout << "Elemento en posición " << i << " no es dict" << std::endl;
                continue;
            }
            py::dict card = cards[i].cast<py::dict>();
            // for (auto item : card) {
            //     std::cout << "Key: " << std::string(py::str(item.first)) << " | Value type: " << std::string(py::str(item.second.get_type())) << std::endl;
            // }
            if (!card.contains("power_level") || !card.contains("rank")) {
                std::cout << "Falta clave en el dict en posición " << i << std::endl;
                continue;
            }
            try {
                long long power_level = card["power_level"].cast<long long>();
                std::uniform_int_distribution<long long> dis(1, power_level);
                if (dis(gen) == 1) {
                    candidates.push_back(i);
                }
            } catch (const std::exception& e) {
                std::cout << "Excepción al castear power_level en posición " << i << ": " << e.what() << std::endl;
                std::cout << "Valor problemático: " << std::string(py::str(card["power_level"])) << std::endl;
                continue;
            }
        }
        if (!candidates.empty()) {
            std::uniform_int_distribution<size_t> dis(0, candidates.size() - 1);
            int selected_index = candidates[dis(gen)];
            py::dict selected_card = cards[selected_index].cast<py::dict>();
            try {
                return selected_card["rank"].cast<int>();
            } catch (const std::exception& e) {
                std::cout << "Excepción al castear rank en el elemento seleccionado: " << e.what() << std::endl;
                std::cout << "Valor problemático: " << std::string(py::str(selected_card["rank"])) << std::endl;
                return -1;
            }
        }
        // Si no hay candidatas, repite el roll
    }
}

PYBIND11_MODULE(roll_card, m) {
    m.def("roll_card", &roll_card, "Realiza un roll y devuelve el rank de la carta seleccionada");
}