package me.hackzurich.getcookingnew;

import java.util.ArrayList;

import android.app.Activity;
import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.CheckBox;
import android.widget.TextView;

// here's our beautiful adapter
public class ArrayAdapterItem extends ArrayAdapter<ObjectItem> {

    Context mContext;
    int layoutResourceId;
    ObjectItem data[] = null;
    private String total;

    public ArrayAdapterItem(Context mContext, int layoutResourceId, ObjectItem[] data) {

        super(mContext, layoutResourceId, data);

        this.layoutResourceId = layoutResourceId;
        this.mContext = mContext;
        this.data = data;
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {

        /*
         * The convertView argument is essentially a "ScrapView" as described is Lucas post 
         * http://lucasr.org/2012/04/05/performance-tips-for-androids-listview/
         * It will have a non-null value when ListView is asking you recycle the row layout. 
         * So, when convertView is not null, you should simply update its contents instead of inflating a new row layout.
         */
        if(convertView==null){
            // inflate the layout
            LayoutInflater inflater = ((Activity) mContext).getLayoutInflater();
            convertView = inflater.inflate(layoutResourceId, parent, false);
        }

        // object item based on the position
        final ObjectItem objectItem = data[position];

        // get the TextView and then set the text (item name) and tag (item ID) values
        TextView textViewItem = (TextView) convertView.findViewById(R.id.textViewItem);
        final CheckBox checkBoxItem = (CheckBox) convertView.findViewById(R.id.checkBoxItem);
        TextView priceItem = (TextView) convertView.findViewById(R.id.priceItem);
        priceItem.setText(formatPrice(objectItem.price));
        textViewItem.setText(objectItem.itemName);
        //textViewItem.setTag(objectItem.itemId);
        if(objectItem.bought) {
        	checkBoxItem.setChecked(true);
        } else {
        	checkBoxItem.setChecked(false);
        }
        checkBoxItem.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                objectItem.bought = checkBoxItem.isChecked();
                notifyDataSetChanged();
            }
        });
        convertView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                checkBoxItem.setChecked(!checkBoxItem.isChecked());
                objectItem.bought = checkBoxItem.isChecked();
                notifyDataSetChanged();
            }
        });

        return convertView;

    }
    
    @Override
    public int getCount() {
    	return this.data.length;
    }

    public ObjectItem addObject(String ean) {
        ObjectItem item = new ObjectItem(ean, ean);
        item.bought = true;
    	data = java.util.Arrays.copyOf(data, data.length + 1);
    	data[data.length - 1] = item;
        return item;
    }


    public boolean checkByEAN(String ean) {
        for(ObjectItem item:data){
            if(item.eans.contains(ean)){
                item.bought = true;
                notifyDataSetChanged();
                return true;
            }
        }
        return false;
    }

    public String getTotal() {
        int counter = 0;
        for(ObjectItem item:data){
            if(item.bought) {
                counter += item.price;
            }
        }
        return formatPrice(counter);
    }

    private String formatPrice(int counter) {
        return String.format("%10.2f CHF", counter/100.0f);
    }
}