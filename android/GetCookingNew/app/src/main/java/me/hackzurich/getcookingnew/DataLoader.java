package me.hackzurich.getcookingnew;

import java.io.IOException;
import java.net.URI;

import org.apache.http.HttpResponse;
import org.apache.http.HttpStatus;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpDelete;
import org.apache.http.client.methods.HttpEntityEnclosingRequestBase;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.params.BasicHttpParams;
import org.apache.http.params.HttpParams;
import org.apache.http.util.EntityUtils;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import android.os.AsyncTask;

public class DataLoader {

	public DataLoader() {
	}

	public void getShoppingList(ShoppingListLoaderListener listener) {
		new DownloadShoppingList(listener).execute("http://hackzurich.me/shopping_list");
	}
	public interface ShoppingListLoaderListener {
		public void onShoppingListAvailable(ObjectItem[] objectItemData);
	}

	private class DownloadShoppingList extends AsyncTask<String, Void, JSONObject> {

		private ShoppingListLoaderListener listener;

		public DownloadShoppingList(ShoppingListLoaderListener listener) {
			this.listener = listener;
		}

		@Override
		protected JSONObject doInBackground(String... params) {
			String content = getContent(params[0]);
			if(content == null)
				return null;
			try {
				JSONObject reader = new JSONObject(content);
				return reader;
			} catch (JSONException e) {
				e.printStackTrace();
				return null;
			}

		}

		@Override
		protected void onPostExecute(JSONObject result) {
			super.onPostExecute(result);

			ObjectItem[] objectItemData = null;

			try {
				JSONArray items;
				items = result.getJSONArray("ingredients");
				objectItemData = new ObjectItem[items.length()];
				for (int i = 0; i < items.length(); i++) {
					JSONObject obj = items.getJSONObject(i);
					objectItemData[i] = new ObjectItem(obj.getInt("id"),obj.getString("title"), obj.getJSONArray("eans"), obj.getInt("price"));
				}
			} catch (JSONException e) {
				objectItemData = null;
				e.printStackTrace();
			} catch (Exception e) {
				objectItemData = null;
			}

			listener.onShoppingListAvailable(objectItemData);

		}

	}













    public void getIngredientName(UpdateListenener listener, String barCode) {
        new DownloadIngredientName(listener).execute("http://hackzurich.me/ingredient/" + barCode);
    }
    public interface UpdateListenener {
        public void onUpdate(JSONObject update);
    }
    private class DownloadIngredientName extends AsyncTask<String, Void, JSONObject> {

        private UpdateListenener listener;

        public DownloadIngredientName(UpdateListenener listener) {
            this.listener = listener;
        }

        @Override
        protected JSONObject doInBackground(String... params) {
            String content = getContent(params[0]);
            if(content == null)
                return null;
            try {
                JSONObject reader = new JSONObject(content);
                return reader;
            } catch (JSONException e) {
                e.printStackTrace();
                return null;
            }

        }

        @Override
        protected void onPostExecute(JSONObject result) {
            super.onPostExecute(result);

            try {
                JSONObject obj = result.getJSONObject("ingredient");
                listener.onUpdate(obj);
            } catch (JSONException e) {
                e.printStackTrace();
                listener.onUpdate(null);
            } catch (Exception e) {
                e.printStackTrace();
                listener.onUpdate(null);
            }


        }

    }






    public void buyItems(final DoneListener listener, final JSONArray items) throws JSONException {

        final JSONObject data = new JSONObject();
        data.put("inventory",items);
        final JSONObject data2 = new JSONObject();
        data2.put("ingredients",items);


        new PostRequest(new DoneListener() {
            @Override
            public void onDone() {
                new PostRequest(listener, data2).execute("http://hackzurich.me/shopping_list/delete");
            }
        },data).execute("http://hackzurich.me/inventory");
    }
    public interface DoneListener {
        public void onDone();
    }
    private class PostRequest extends AsyncTask<String, Void, JSONObject> {

        private DoneListener listener;
        private Object items;

        public PostRequest(DoneListener listener, Object items) {
            this.listener = listener;
            this.items = items;
        }

        @Override
        protected JSONObject doInBackground(String... params) {
            String content = postContent(params[0], items);
            if(content == null)
                return null;
            try {
                JSONObject reader = new JSONObject(content);
                return reader;
            } catch (JSONException e) {
                e.printStackTrace();
                return null;
            }

        }

        @Override
        protected void onPostExecute(JSONObject result) {
            super.onPostExecute(result);

            try {
                listener.onDone();
            } catch (Exception e) {
                e.printStackTrace();
                listener.onDone();
            }


        }

    }
    private String postContent(String url, Object items) {
        HttpResponse response = null;
        HttpPost httpPost = null;
        HttpClient mHttpClient = null;
        String s = null;

        try {
            if(mHttpClient == null) {
                HttpParams httpParams = new BasicHttpParams();
                //HttpConnectionParams.setConnectionTimeout(httpParams, mTimoutInSeconds * 1000);
                //HttpConnectionParams.setSoTimeout(httpParams, mTimoutInSeconds * 1000);
                mHttpClient = new DefaultHttpClient(httpParams);
            }
            httpPost = new HttpPost(url);
            StringEntity  postingString =new StringEntity(items.toString());//convert your pojo to   json
            httpPost.setEntity(postingString);
            httpPost.setHeader("Content-type", "application/json");
            response = mHttpClient.execute(httpPost);
            if (response != null && response.getStatusLine().getStatusCode() == HttpStatus.SC_OK) {
                s = EntityUtils.toString(response.getEntity(), "UTF-8");
            } else {
                s = null;
            }

        } catch (IOException e) {
            e.printStackTrace();
            s = null;
        }

        return s;
    }
    private String getContent(String url) {
		HttpResponse response = null;
		HttpGet httpGet = null;
		HttpClient mHttpClient = null;
		String s = null;

		try {
			if(mHttpClient == null) {
				HttpParams httpParams = new BasicHttpParams();
				//HttpConnectionParams.setConnectionTimeout(httpParams, mTimoutInSeconds * 1000);
				//HttpConnectionParams.setSoTimeout(httpParams, mTimoutInSeconds * 1000);
				mHttpClient = new DefaultHttpClient(httpParams);
			}
			httpGet = new HttpGet(url);

			response = mHttpClient.execute(httpGet);
			if (response != null && response.getStatusLine().getStatusCode() == HttpStatus.SC_OK) {
				s = EntityUtils.toString(response.getEntity(), "UTF-8");
			} else {
				s = null;
			}

		} catch (IOException e) {
			e.printStackTrace();
			s = null;
		} 

		return s;
	}
}
