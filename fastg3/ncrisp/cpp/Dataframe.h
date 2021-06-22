#ifndef DATAFRAME_H
#define DATAFRAME_H

#include <vector>
#include <variant>
#include <unordered_map>
#include <string>
#include <ostream>
#include <string>

#include "NumAttribute.h"
#include "StrAttribute.h"

using attr_types = std::variant<NumAttribute<long>, NumAttribute<double>, StrAttribute>;
using attr_list = std::vector<std::string>;
using attr_map = std::unordered_map<std::string, size_t>;

using vp_type = std::pair<size_t,size_t>;
using vp_list = std::vector<vp_type>;

class Dataframe{
public:
    // ------ Constructor
    /**
     * Constructor of dataframe
     *
     * @param pindex original user index
     * @param pnrows number or rows
     * @return nothing
     */
    Dataframe(size_t* pindex, size_t pnrows);

    /**
     * Returns a vector of all the column contained by the dataframe.
     *
     * @return vector of column names
     */
    attr_list get_columns();

    /**
     * Gives the number of rows of the dataframe.
     *
     * @return number of rows
     */
    size_t get_n_rows() const;

    // ------ General dataframe methods
    /**
     * Adds a numerical column of specified type in the dataframe.
     * The column in then copied within a NumAttribute class.
     *
     * @param name Name of the column.
     * @param attr Array of specified type.
     * @param metric Metric for comparing two values of the column.
     * @param thresold Thresold under which two values of the column are considered similar under the metric.
     * @return nothig
     */
    template <typename T>
    void add_column(std::string name, T * attr, std::string metric, double threshold);

    /**
     * Adds a string column of specified type in the dataframe.
     * The column in then copied within a StrAttribute class.
     *
     * @param name Name of the column.
     * @param attr Array of specified type.
     * @param metric Metric for comparing two values of the column.
     * @param thresold Thresold under which two values of the column are considered similar under the metric.
     * @return nothig
     */
    void add_str_column(std::string name, std::vector<std::string> attr, std::string metric, double threshold);

    /**
     * Displays the column of given name on the standard output.
     *
     * @param name Name of the column.
     * @return nothig
     */
    void show_col(std::string col_name);

    /**
     * Displays the value of a given column on the standard output.
     *
     * @param name Name of the column.
     * @param i Index to display in the column.
     * @return nothig
     */
    void show_val(std::string col_name, size_t i);

    /**
     * Displays a row
     *
     * @param i Index of the row to display.
     * @return nothig
     */
    void show_row(size_t i, bool header);

    /**
     * Gives the corresponding original user index.
     *
     * @return number of rows
     */
    size_t get_user_index(size_t i) const;

    /**
     * Reutrns the original user index.
     *
     * @return user index as a vector
     */
    std::vector<size_t> get_user_index() const;

    /**
     * For an user index, returns the absolute index in memory.
     *
     * @return memory index
     */
    size_t get_mem_from_user_index(size_t i);

    // ------ Join methods
    void set_block_index(std::vector<long> input);
    long get_block_index(size_t i);
    bool is_attr_similar(std::string col_name, size_t index_i, size_t index_j);
    bool is_vp(size_t i, size_t j, attr_list x_attrs, attr_list y_attrs);

    vp_list bf_join(std::vector<size_t> block, attr_list x_attrs, attr_list y_attrs);
    vp_list ordered_join(std::vector<size_t> block, attr_list x_attrs, attr_list y_attrs);
    std::vector<size_t> bf_row_join(std::vector<size_t> block, size_t row, attr_list x_attrs, attr_list y_attrs);
    std::vector<size_t> ordered_row_join(std::vector<size_t> block, size_t row, attr_list x_attrs, attr_list y_attrs);

private:
    // attributes for handling column names
    attr_map cols_map; // unordered map of column names to indices for attributes

    // attributes for handling dataframe
    size_t n_rows; // number of rows
    std::vector<attr_types> attributes; // vector of attributes of the dataframe

    // blocking
    std::vector<long> block_index; // stores the block_number of each row
    std::vector<long> block_pos; // stores the position inside the block for each row

    // user index back and forth : index<->memory
    std::vector<size_t> user_index; // stores the original user index
    std::unordered_map<size_t,size_t> user_index_map;
};

/////////////////////////////////////////////////////// DEFINITION

//~~~~~~~~~~~ Constructor
Dataframe::Dataframe(size_t* pindex, size_t pnrows): n_rows(pnrows){
    for(size_t i = 0; i < n_rows; i++){
        user_index.push_back(pindex[i]);
        user_index_map[pindex[i]]=i;
    }
}

//~~~~~~~~~~~ General dataframe methods
template <typename T>
void Dataframe::add_column(std::string name, T * attr, std::string metric, double threshold){
    attributes.push_back(NumAttribute<T>(attr, n_rows, metric, threshold));
    cols_map[name] = attributes.size()-1;
}

void Dataframe::add_str_column(std::string name, std::vector<std::string> attr, std::string metric, double threshold){
    attributes.push_back(StrAttribute(attr, n_rows, metric, threshold));
    cols_map[name] = attributes.size()-1;
}

void Dataframe::show_col(std::string col_name){
    std::visit([](auto&& arg) -> void 
    {
        arg.show_col();
    }, attributes[cols_map[col_name]]);
}

void Dataframe::show_val(std::string col_name, size_t i){
    std::variant<size_t> index(i);
    std::visit([](auto&& arg, size_t index) -> void 
    {
        arg.show_val(index);
    }, attributes[cols_map[col_name]], index);
}

void Dataframe::show_row(size_t i, bool header=true){
    attr_list attrs = get_columns();
    if(header){
        std::cout << "[index";
        for(size_t attr_i=0; attr_i<attrs.size(); attr_i++){
            std::cout << " " << attrs[attr_i];
        }
        std::cout << "]" << std::endl;
    }
    std::cout << i << " ";
    for(size_t attr_i=0; attr_i<attrs.size(); attr_i++){
        std::string attr =  attrs[attr_i];
        show_val(attr, i);
        std::cout << " ";
    }
    std::cout << std::endl;
}

size_t Dataframe::get_n_rows() const{
    return n_rows;
}

size_t Dataframe::get_user_index(size_t i) const{
    return user_index[i];
}

std::vector<size_t> Dataframe::get_user_index() const{
    return user_index;
}

attr_list Dataframe::get_columns(){
    attr_list cols;
    for(attr_map::iterator it = cols_map.begin(); it != cols_map.end(); ++it) {
        cols.push_back(it->first);
    }
    return cols;
}

size_t Dataframe::get_mem_from_user_index(size_t i){
    std::unordered_map<size_t,size_t>::iterator it = user_index_map.find(i);
    if (user_index_map.find(i) == user_index_map.end()) {
        throw std::out_of_range("Unknown index "+std::to_string(i)+" : not existing or may have been dropped during pandas dropna().");
    }
    return it->second;
}

//~~~~~~~~~~~ Join methods
void Dataframe::set_block_index(std::vector<long> in){
    std::unordered_map<long, long> um;
    long block_num = 0;
    for(size_t i=0; i<in.size(); i++){
        block_num = in[i];
        if(um.find(block_num)==um.end()) um[block_num]=-1;
        block_index.push_back(block_num);
        block_pos.push_back(++um[block_num]);
    }
}

long Dataframe::get_block_index(size_t i){
    return block_index[i];
}

bool Dataframe::is_attr_similar(std::string col_name, size_t index_i, size_t index_j){
    std::variant<size_t> i(index_i);
    std::variant<size_t> j(index_j);
    bool a = std::visit([](auto&& arg, size_t i, size_t j) -> bool 
    {
        return arg.is_similar(i,j);
    }, attributes[cols_map[col_name]], i, j);
    return a;
}

bool Dataframe::is_vp(size_t i, size_t j, attr_list x_attrs, attr_list y_attrs){
    std::vector<std::string>::iterator vec_it = x_attrs.begin();
    while(vec_it != x_attrs.end() && is_attr_similar(*vec_it, i, j)) vec_it++;
    if(vec_it == x_attrs.end()){
        vec_it = y_attrs.begin();
        while(vec_it != y_attrs.end() && is_attr_similar(*vec_it, i, j)) vec_it++;
        if(vec_it != y_attrs.end()) return true;
    }
    return false;
}

vp_list Dataframe::bf_join(std::vector<size_t> block, attr_list x_attrs, attr_list y_attrs){
    vp_list vps;
    for(size_t i=0; i<block.size()-1; i++){
        for(size_t j=i+1; j<block.size(); j++){
            if(is_vp(block[i], block[j], x_attrs, y_attrs)){
                vps.push_back(vp_type(get_user_index(block[i]), get_user_index(block[j])));
            }
        }
    }
    return vps;
}

vp_list Dataframe::ordered_join(std::vector<size_t> block, attr_list x_attrs, attr_list y_attrs){
    vp_list vps;
    size_t j=0;
    size_t k;
    for(size_t i=0; i<block.size()-1; i++){
        std::cout << get_user_index(block[i]) << std::endl;
        while(j<block.size() && j<=i) j++;
        if(j>i){
            while(j<block.size() && is_attr_similar(x_attrs[0], block[i], block[j])) j++;
            for(k=i+1; k<j; k++){
                if(x_attrs.size()==1 or is_vp(block[i], block[k], attr_list(x_attrs.begin()+1, x_attrs.end()), y_attrs)){
                    vps.push_back(vp_type(get_user_index(block[i]), get_user_index(block[k])));
                }
            }
        }
    }
    return vps;
}

std::vector<size_t> Dataframe::bf_row_join(std::vector<size_t> block, size_t row_index, attr_list x_attrs, attr_list y_attrs){
    std::vector<size_t> neighbors;
    for(size_t i=0; i<block.size(); i++){
        if(block[i]!=row_index && is_vp(row_index, block[i], x_attrs, y_attrs)){
            neighbors.push_back(get_user_index(block[i]));
        }
    }
    return neighbors;
}

std::vector<size_t> Dataframe::ordered_row_join(std::vector<size_t> block, size_t row_index, attr_list x_attrs, attr_list y_attrs){
    std::vector<size_t> neighbors;
    size_t bp = block_pos[row_index];
    if(bp<block.size()-1){
        for(size_t i=bp+1; i<block.size() && is_attr_similar(x_attrs[0], row_index, block[i]); i++){
            if(is_vp(row_index, block[i], attr_list(x_attrs.begin()+1, x_attrs.end()), y_attrs)){
                neighbors.push_back(get_user_index(block[i]));
            }
        }
    }
    for(long i=bp-1; i>=0 && is_attr_similar(x_attrs[0], row_index, block[i]); i--){
        if(is_vp(row_index, block[i], attr_list(x_attrs.begin()+1, x_attrs.end()), y_attrs)){
            neighbors.push_back(get_user_index(block[i]));
        }
    }
    return neighbors;
}

#endif