package eheritage;

import java.util.Collection;

import org.elasticsearch.common.inject.Module;
import org.elasticsearch.plugins.AbstractPlugin;

import com.google.common.collect.Lists;

public class ExtractNamesPlugin extends AbstractPlugin {

    @Override
    public String name() {
      return "extract-names-plugin";
    }

    @Override
    public String description() {
      return "extract names from unstructed texts of a document using Apache OpenNLP";
    }

    @Override
    public Collection<Class<? extends Module>> modules() {
      Collection<Class<? extends Module>> modules = Lists.newArrayList();
      modules.add(ExtractNamesModule.class);
      return modules;
    }
}
